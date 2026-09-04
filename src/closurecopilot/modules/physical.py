"""Module 5 — Physical-Aware RTL Feedback.

Reads place-and-route congestion/utilization reports and feeds back RTL restructuring
hints — bridging the physical → RTL gap that synthesis/STA-only agents miss.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..models import Finding, Fix, AnalysisItem, LAYER_RTL


def analyze(text: str, source: str = "congestion.rpt") -> list:
    items = []
    for line in text.splitlines():
        m = re.match(r"\s+(\w+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+(yes|no)", line)
        if not m:
            continue
        blk, util, peak, overflow, hotspot = (m.group(1), float(m.group(2)),
                                              float(m.group(3)), int(m.group(4)), m.group(5))
        if hotspot == "yes" or peak >= 85.0 or overflow > 0:
            sev = "High" if peak >= 95.0 or overflow >= 150 else "Medium"
            f = Finding("physical",
                f"Routing congestion hotspot in {blk}", sev, location=blk,
                detail=f"Peak congestion {peak:.0f}% (util {util:.0f}%, overflow {overflow} "
                       f"gcells). Physically unfriendly RTL structure.",
                metrics={"peak_congestion_pct": peak, "overflow": overflow, "util_pct": util},
                source=source)
            # tailor the RTL hint by known structure
            if blk == "crc_gen":
                hint = ("Wide XOR tree — pipeline the tree or split into balanced stages so "
                        "routing demand spreads across a register boundary.")
                snip = ("// pipeline the CRC XOR tree\n"
                        "always_ff @(posedge clk) crc_stage <= crc_partial;  // split tree")
            elif blk == "decoder":
                hint = ("Large one-hot decode fanout — register the decode or restructure to "
                        "reduce net fanout / spread drivers.")
                snip = ("// register decode outputs to cut fanout congestion\n"
                        "always_ff @(posedge clk) dec_q <= decode_comb;")
            else:
                hint = ("High local congestion — restructure or pipeline the dense "
                        "combinational logic; consider logic sharing.")
                snip = "// restructure / pipeline the dense combinational cone"
            fx = Fix(LAYER_RTL, rationale=hint, snippet=snip,
                     tradeoff={"timing": "improves (shorter nets)", "power": "minor",
                               "area": "+minor (regs)", "note": "eases congestion; +1 cycle latency"},
                     confidence=0.75, references=["global:High utilization / congestion"])
            items.append(AnalysisItem(f, fx))
    return items


def run_on_samples(samples_dir) -> list:
    p = Path(samples_dir) / "congestion.rpt"
    return analyze(p.read_text(encoding="utf-8", errors="ignore"))
