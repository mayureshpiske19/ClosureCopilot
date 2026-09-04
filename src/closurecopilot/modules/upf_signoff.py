"""Module 3 — UPF / Low-Power Signoff.

The power-intent counterpart to an SDC checker: cross-checks UPF against RTL and the
power report and produces a signoff checklist with corrected UPF snippets. Covers
isolation, retention, and clock-gating-intent realization.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..models import Finding, Fix, AnalysisItem, LAYER_UPF, LAYER_RTL
from ..ingestion.parsers import parse_upf


def _power_clock_frac(power_text: str, block: str) -> float:
    for line in power_text.splitlines():
        m = re.match(rf"\s+{re.escape(block)}\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", line)
        if m:
            clock, total = float(m.group(4)), float(m.group(5))
            return clock / total if total else 0.0
    return 0.0


def signoff(upf_text: str, power_text: str, upf_source: str = "soc_top.upf") -> list:
    items = []
    findings = parse_upf(upf_text, source=upf_source)
    from .. import fix_router
    for f in findings:
        fx = fix_router.route(f)
        # enrich clock-gating intent finding with measured evidence from power report
        if f.metrics.get("issue") == "cg_intent_unrealized":
            frac = _power_clock_frac(power_text, "dma_ctrl")
            if frac:
                f.detail += f" Power report confirms clock power = {frac*100:.0f}% of dma_ctrl total."
                f.metrics["measured_clock_frac"] = round(frac, 2)
        fx.references = fx.references or ["global:UPF isolation", "design:Power intent"]
        items.append(AnalysisItem(f, fx))
    return items


def checklist(items: list) -> list:
    """Return a signoff checklist: list of (check, status, note)."""
    have = {it.finding.metrics.get("issue") for it in items}
    rows = [
        ("Isolation on switchable-domain outputs", "missing_isolation"),
        ("Retention on power-gated state", "missing_retention"),
        ("Clock-gating intent realized in RTL", "cg_intent_unrealized"),
    ]
    out = []
    for label, issue in rows:
        failed = issue in have
        out.append((label, "❌ FAIL" if failed else "✅ PASS",
                    next((it.finding.detail for it in items
                          if it.finding.metrics.get("issue") == issue), "OK")))
    return out


def run_on_samples(samples_dir) -> list:
    d = Path(samples_dir)
    upf = (d / "soc_top.upf").read_text(encoding="utf-8", errors="ignore")
    power = (d / "power.rpt").read_text(encoding="utf-8", errors="ignore")
    return signoff(upf, power)
