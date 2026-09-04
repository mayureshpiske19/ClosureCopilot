"""Module 2 — Constraint Promotion & Reconciliation (IP → top).

Reconciles block/IP-level SDC against the integrator's top SDC and flags:
  * clock period / name mismatches between block and top,
  * relaxed or tightened budgets,
  * block exceptions (false_path / multicycle) not promoted to top.
Emits corrected top-level constraint snippets.  (Verified-novel: no internal prior art.)
"""
from __future__ import annotations

import re
from pathlib import Path

from ..models import Finding, Fix, AnalysisItem, LAYER_SDC


def _clocks(text: str) -> dict:
    out = {}
    for m in re.finditer(r"create_clock\s+-name\s+(\S+)\s+-period\s+([\d.]+)", text):
        out[m.group(1)] = float(m.group(2))
    return out


def _exceptions(text: str) -> list:
    ex = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("set_false_path") or s.startswith("set_multicycle_path"):
            ex.append(s)
    return ex


def reconcile(block_texts: dict, top_text: str) -> list:
    """block_texts: {ip_name: sdc_text}; top_text: top sdc. Returns list[AnalysisItem]."""
    items = []
    top_clocks = _clocks(top_text)
    top_ex = _exceptions(top_text)

    for ip, btext in block_texts.items():
        # --- clock reconciliation ---
        for bclk, bper in _clocks(btext).items():
            # direct name match with different period
            if bclk in top_clocks and abs(top_clocks[bclk] - bper) > 1e-6:
                sev = "High" if abs(top_clocks[bclk] - bper) / bper >= 0.2 else "Medium"
                f = Finding("promotion",
                    f"Clock period mismatch on {bclk} ({ip})", sev, location=ip,
                    detail=f"Block '{ip}' constrains {bclk} at {bper:.2f}ns but top defines "
                           f"{top_clocks[bclk]:.2f}ns.",
                    metrics={"block_ns": bper, "top_ns": top_clocks[bclk]},
                    source=f"{ip}.sdc")
                fx = Fix(LAYER_SDC,
                    rationale="Reconcile the block budget with the true top clock and "
                              "re-derive I/O delays against it.",
                    snippet=f"# promote {bclk} for {ip} to the top budget\n"
                            f"create_clock -name {bclk} -period {top_clocks[bclk]:.2f} "
                            f"[get_ports {bclk}]\n"
                            f"# re-budget block I/O delays to the {top_clocks[bclk]:.2f}ns clock",
                    tradeoff={"timing": "re-budgeted", "power": "none", "area": "none"},
                    confidence=0.85, references=["global:Constraint promotion (IP → subsystem → top)"])
                items.append(AnalysisItem(f, fx))
            # block clock not present at top at all (e.g. clk_usb driven by clk_120m)
            if bclk not in top_clocks:
                f = Finding("promotion",
                    f"Block clock '{bclk}' not defined at top ({ip})", "High", location=ip,
                    detail=f"'{ip}' assumes {bclk} ({bper:.2f}ns); top has no matching clock — "
                           f"the IP is driven by a different top clock. Map and re-budget.",
                    metrics={"block_ns": bper}, source=f"{ip}.sdc")
                fx = Fix(LAYER_SDC,
                    rationale="Map the IP's clock onto the real top clock net and drop the "
                              "stale block clock definition; re-budget I/O delays.",
                    snippet=f"# {ip}: replace stale '{bclk}' with the real top clock\n"
                            f"# e.g. usb_ip driven by clk_120m (8.33ns):\n"
                            f"set_input_delay  <budget> -clock <top_clk> [get_ports {ip}_*]\n"
                            f"set_output_delay <budget> -clock <top_clk> [get_ports {ip}_*]",
                    tradeoff={"timing": "re-budgeted", "power": "none", "area": "none"},
                    confidence=0.8, references=["global:Constraint promotion (IP → subsystem → top)"])
                items.append(AnalysisItem(f, fx))

        # --- exception promotion ---
        for ex in _exceptions(btext):
            head = ex.split("-from")[0].strip()
            if not any(head in t for t in top_ex):
                kind = "false_path" if "false_path" in ex else "multicycle path"
                f = Finding("promotion",
                    f"Block {kind} not promoted to top ({ip})", "Medium", location=ip,
                    detail=f"Exception defined in {ip} block SDC is missing at top: `{ex}`",
                    source=f"{ip}.sdc", metrics={"exception": ex})
                fx = Fix(LAYER_SDC,
                    rationale="Valid block-level timing exception is lost at integration — "
                              "promote it to the top SDC (re-scoped to top instance path).",
                    snippet=f"# promote from {ip} block SDC to top\n{ex}",
                    tradeoff={"timing": "cleans/re-enables exception", "power": "none", "area": "none"},
                    confidence=0.8, references=["global:Constraint promotion (IP → subsystem → top)"])
                items.append(AnalysisItem(f, fx))
    return items


def run_on_samples(samples_dir) -> list:
    d = Path(samples_dir) / "blocks"
    blocks = {}
    for name in ("usb_ip", "dma_ip"):
        p = d / f"{name}.sdc"
        if p.exists():
            blocks[name] = p.read_text(encoding="utf-8", errors="ignore")
    top = (d / "top_soc.sdc").read_text(encoding="utf-8", errors="ignore")
    return reconcile(blocks, top)
