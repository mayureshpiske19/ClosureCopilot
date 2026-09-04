"""Fix-Routing / Diagnosis engine.

The senior-engineer judgment: for each Finding, decide whether the fix belongs in RTL,
constraints (SDC), UPF, or synthesis setup — and produce a corrected snippet plus a
cross-domain PPA trade-off. Deterministic rules keyed off parsed metrics; RAG context
and (optionally) the LLM enrich the rationale in the agents layer.
"""
from __future__ import annotations

from .models import Finding, Fix, LAYER_RTL, LAYER_SDC, LAYER_UPF, LAYER_SYNTH


def route(f: Finding) -> Fix:
    d, loc, m = f.domain, f.location, f.metrics
    detail = f.detail.lower()

    # ---- TIMING -----------------------------------------------------------
    if d == "timing":
        # Config / quasi-static path -> constraints (multicycle), NOT RTL.
        if "config" in detail or "cfg" in loc.lower() or "once per" in detail:
            return Fix(LAYER_SDC,
                rationale="Quasi-static configuration path treated as single-cycle. "
                          "This is a constraint gap, not a logic bug — add a multicycle path.",
                snippet="set_multicycle_path -setup 2 -from [get_pins cfg_reg*/CK] "
                        "-to [get_pins status_reg*/D]\n"
                        "set_multicycle_path -hold  1 -from [get_pins cfg_reg*/CK] "
                        "-to [get_pins status_reg*/D]",
                tradeoff={"timing": "resolved", "power": "none", "area": "none"},
                confidence=0.9)
        # IP->top clock mismatch -> constraint promotion.
        if "clk_usb" in detail or "maps port" in detail or "period mismatch" in detail:
            return Fix(LAYER_SDC,
                rationale="Block-level clock period does not match the real top clock. "
                          "Promote the IP clock and re-budget I/O delays at top.",
                snippet="# reconcile usb_ip clock at top\n"
                        "create_clock -name clk_120m -period 8.33 [get_ports clk_120m]\n"
                        "set_case_analysis / remap: drive usb_ip on clk_120m, not clk_usb\n"
                        "set_input_delay  1.6 -clock clk_120m [get_ports usb_*]\n"
                        "set_output_delay 1.6 -clock clk_120m [get_ports usb_*]",
                tradeoff={"timing": "re-budgeted", "power": "none", "area": "none"},
                confidence=0.8)
        # Genuine deep combinational logic -> RTL pipeline.
        depth = m.get("logic_depth", 0)
        if depth >= 20 or "deep combinational" in detail or "pipeline" in detail:
            return Fix(LAYER_RTL,
                rationale=f"Genuine deep combinational cone (logic depth {depth}). "
                          "Constraints are correct — pipeline the datapath in RTL.",
                snippet="// insert a pipeline register to split the cone\n"
                        "always_ff @(posedge clk_core) res_stage <= res_comb;\n"
                        "// then register the final result one cycle later",
                tradeoff={"timing": "resolved", "power": "+~1%", "area": "+~2%",
                          "note": "adds 1 cycle latency — confirm architecturally"},
                confidence=0.85)
        return Fix(LAYER_SDC, rationale="Review path exceptions before RTL changes.",
                   snippet="# inspect clock/exception definitions for this path",
                   tradeoff={"timing": "investigate"}, confidence=0.5)

    # ---- POWER ------------------------------------------------------------
    if d == "power":
        if m.get("clock_frac", 0) >= 0.4 or "ungated" in detail:
            return Fix(LAYER_RTL,
                rationale="Clock power dominates because registers are not gated. UPF "
                          "intends clock gating but the enable is not expressed in RTL, so "
                          "no ICG is inferred. Guard the register with the activity enable.",
                snippet="// dma_ctrl.sv — guard update so an ICG is inferred\n"
                        "always_ff @(posedge clk)\n"
                        "  if (dma_active)\n"
                        "    buf_q <= wdata;",
                tradeoff={"timing": "none", "power": "large clock-power reduction",
                          "area": "negligible (+ICG)"},
                confidence=0.9)
        return Fix(LAYER_RTL,
            rationale="Dynamic switching hotspot — apply operand isolation / enable-based "
                      "gating so idle cycles stop toggling.",
            snippet="// isolate operands when unit is idle\n"
                    "assign a_gated = enable ? a : a_hold;",
            tradeoff={"timing": "none", "power": "switching reduction", "area": "minor"},
            confidence=0.7)

    # ---- AREA -------------------------------------------------------------
    if d == "area":
        return Fix(LAYER_RTL,
            rationale="Block over ~85% utilization risks routing congestion. Large "
                      "combinational trees (e.g. XOR/adder) should be pipelined or "
                      "restructured / shared in RTL.",
            snippet="// pipeline / restructure the wide combinational tree\n"
                    "// split the XOR tree across a register stage to ease congestion",
            tradeoff={"timing": "improves", "power": "minor", "area": "+minor (regs)",
                      "note": "eases congestion; adds 1 cycle latency"},
            confidence=0.75)

    # ---- SYNTHESIS --------------------------------------------------------
    if d == "synthesis":
        issue = m.get("issue")
        if issue == "unmapped_cells":
            return Fix(LAYER_SYNTH,
                rationale="Operator has no matching library cell. Point synthesis at a lib "
                          "that contains it, or decompose the operator in RTL.",
                snippet="# synthesis setup\nset_db library {tech_lib_with_XOR4.lib}\n"
                        "# or RTL: build a balanced XOR tree from XOR2 primitives",
                tradeoff={"timing": "improves", "power": "minor", "area": "improves"},
                confidence=0.8)
        if issue == "inferred_latch":
            return Fix(LAYER_RTL,
                rationale="Incomplete case/if inferred a latch. Add a default assignment so "
                          "the signal is always driven.",
                snippet="always_comb begin\n  state_next = state;   // default\n"
                        "  unique case (state)\n    ...\n    default: state_next = IDLE;\n"
                        "  endcase\nend",
                tradeoff={"timing": "improves", "power": "improves", "area": "none"},
                confidence=0.9)
        if issue in ("cg_missing", "cg_opportunity"):
            return Fix(LAYER_RTL,
                rationale="Clock-gating enable not visible to the tool. Express the enable "
                          "as a register guard so ICGs are inferred.",
                snippet="always_ff @(posedge clk) if (enable) q <= d;",
                tradeoff={"timing": "none", "power": "clock-power reduction", "area": "minor"},
                confidence=0.8)

    # ---- UPF --------------------------------------------------------------
    if d == "upf":
        issue = m.get("issue")
        if issue == "missing_isolation":
            return Fix(LAYER_UPF,
                rationale="Switchable-domain outputs cross to always-on logic without "
                          "isolation — they float when powered down. Add isolation.",
                snippet="set_isolation iso_dma -domain PD_DMA "
                        "-isolation_power_net VDD_AO -clamp_value 0 -applies_to outputs\n"
                        "set_isolation_control iso_dma -domain PD_DMA "
                        "-isolation_signal iso_en -isolation_sense high",
                tradeoff={"timing": "none", "power": "enables safe power gating",
                          "area": "minor (iso cells)"},
                confidence=0.9)
        if issue == "missing_retention":
            return Fix(LAYER_UPF,
                rationale="State registers need to survive power-down — add a retention "
                          "strategy to PD_USB.",
                snippet="set_retention ret_usb -domain PD_USB -retention_power_net VDD_AO\n"
                        "set_retention_control ret_usb -domain PD_USB "
                        "-save_signal save -restore_signal restore",
                tradeoff={"timing": "none", "power": "enables retention", "area": "minor"},
                confidence=0.8)
        if issue == "cg_intent_unrealized":
            return Fix(LAYER_RTL,
                rationale="UPF clock-gating intent is correct but unrealized — the fix is in "
                          "RTL: wire the enable so an ICG is inferred (see dma_ctrl.sv:142).",
                snippet="always_ff @(posedge clk) if (dma_active) buf_q <= wdata;",
                tradeoff={"timing": "none", "power": "large clock-power reduction",
                          "area": "negligible"},
                confidence=0.9)

    # ---- SDC --------------------------------------------------------------
    if d == "sdc":
        issue = m.get("issue")
        if issue == "missing_multicycle":
            return Fix(LAYER_SDC,
                rationale="Config path sampled once per write — add a multicycle exception.",
                snippet="set_multicycle_path -setup 2 -from [get_pins cfg_reg*/CK] "
                        "-to [get_pins status_reg*/D]",
                tradeoff={"timing": "resolved", "power": "none", "area": "none"},
                confidence=0.85)
        if issue == "clock_promotion":
            return Fix(LAYER_SDC,
                rationale="Promote usb_ip block clock to the true top clock and re-budget.",
                snippet="create_clock -name clk_120m -period 8.33 [get_ports clk_120m]\n"
                        "# map usb_ip onto clk_120m; drop stale clk_usb 10.0ns definition",
                tradeoff={"timing": "re-budgeted", "power": "none", "area": "none"},
                confidence=0.8)
        if issue == "missing_false_path":
            return Fix(LAYER_SDC,
                rationale="Static strap signal — exclude with a false path.",
                snippet="set_false_path -from [get_ports test_mode]",
                tradeoff={"timing": "cleans report", "power": "none", "area": "none"},
                confidence=0.8)

    return Fix(LAYER_RTL, rationale="Manual review recommended.", confidence=0.3)
