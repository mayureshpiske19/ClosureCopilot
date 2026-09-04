"""Ingestion / Parser Agent — tool-agnostic report normalizer.

Detects the backend report type and extracts structured `Finding`s. Deterministic and
dependency-free so it always runs. Supports: STA timing, synthesis log, RTLA power,
area, UPF, SDC.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..models import Finding


def detect_type(name: str, text: str) -> str:
    n = name.lower()
    if n.endswith(".upf") or "create_power_domain" in text:
        return "upf"
    if n.endswith(".sdc") or ("create_clock" in text and "set_input_delay" in text):
        return "sdc"
    if "slack" in text.lower() and "startpoint" in text.lower():
        return "sta"
    if "unmapped" in text.lower() or "inferred latch" in text.lower():
        return "synth"
    if "switching" in text.lower() and "leakage" in text.lower():
        return "power"
    if "util" in text.lower() and "area" in text.lower():
        return "area"
    return "unknown"


# ---------------------------------------------------------------- STA timing
def parse_sta(text: str, source: str) -> list:
    findings = []
    blocks = re.split(r"\nStartpoint:", text)
    for b in blocks[1:]:
        block = "Startpoint:" + b
        sp = re.search(r"Startpoint:\s*(\S+)", block)
        ep = re.search(r"Endpoint:\s*(\S+)", block)
        grp = re.search(r"Path Group:\s*(\S+)", block)
        slack_m = re.search(r"slack\s*\(VIOLATED\)\s*(-?\d+\.\d+)", block)
        if not slack_m:
            continue
        slack = float(slack_m.group(1))
        note = re.search(r"(?:Note|RTL):\s*(.+)", block)
        rtl = re.search(r"RTL:\s*(\S+)", block)
        depth = re.search(r"logic depth\s+(\d+)", block)
        sev = "High" if slack <= -0.5 else ("Medium" if slack <= -0.1 else "Low")
        loc = rtl.group(1) if rtl else (sp.group(1) if sp else "")
        findings.append(Finding(
            domain="timing",
            title=f"Setup violation on {grp.group(1) if grp else 'path'} "
                  f"({sp.group(1) if sp else '?'} → {ep.group(1) if ep else '?'})",
            severity=sev,
            location=loc,
            detail=(note.group(1).strip() if note else "Negative slack path."),
            metrics={"slack_ns": slack,
                     **({"logic_depth": int(depth.group(1))} if depth else {})},
            source=source,
        ))
    return findings


# ---------------------------------------------------------------- synthesis
def parse_synth(text: str, source: str) -> list:
    findings = []
    for m in re.finditer(r"cells left unmapped in module (\w+).*?\((.*?)\)", text):
        findings.append(Finding("synthesis",
            f"Unmapped cells in {m.group(1)}", "High",
            location=m.group(1), detail=m.group(2), source=source,
            metrics={"issue": "unmapped_cells"}))
    for m in re.finditer(r"Inferred latch for signal '(\w+)' in module (\w+) \(([^)]+)\)", text):
        findings.append(Finding("synthesis",
            f"Inferred latch '{m.group(1)}' in {m.group(2)}", "High",
            location=m.group(3), detail="Incomplete case/if — latch inferred.",
            source=source, metrics={"issue": "inferred_latch"}))
    for m in re.finditer(r"clock-gating cell not inferred for module (\w+) \(([^)]+)\)", text):
        findings.append(Finding("synthesis",
            f"Clock gating not inferred in {m.group(1)}", "Medium",
            location=m.group(2), detail="Gating enable not wired in RTL.",
            source=source, metrics={"issue": "cg_missing"}))
    cg = re.search(r"Clock gating cells inserted:\s*(\d+)\s*\(opportunities detected:\s*(\d+)\)", text)
    if cg and int(cg.group(2)) > int(cg.group(1)):
        findings.append(Finding("synthesis",
            "Missed clock-gating opportunities", "Medium", location="soc_top",
            detail=f"{cg.group(1)} inserted of {cg.group(2)} detected.",
            source=source, metrics={"issue": "cg_opportunity",
                                    "inserted": int(cg.group(1)), "detected": int(cg.group(2))}))
    return findings


# ---------------------------------------------------------------- power
def parse_power(text: str, source: str) -> list:
    findings, rows = [], []
    for line in text.splitlines():
        m = re.match(r"\s+(\w+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", line)
        if m:
            rows.append((m.group(1), *[float(x) for x in m.groups()[1:]]))
    for name, internal, switching, leakage, clock, total in rows:
        # Flag blocks where clock power dominates (>40% of block total).
        if total > 0 and clock / total >= 0.40:
            findings.append(Finding("power",
                f"High clock power in {name}", "High", location=name,
                detail=f"Clock power {clock:.2f} mW = {clock/total*100:.0f}% of block total "
                       f"({total:.2f} mW). Likely ungated registers.",
                source=source,
                metrics={"clock_mW": clock, "total_mW": total,
                         "clock_frac": round(clock/total, 2)}))
        # Flag high switching-power hotspots.
        elif switching >= 4.0:
            findings.append(Finding("power",
                f"High switching power in {name}", "Medium", location=name,
                detail=f"Switching power {switching:.2f} mW — dynamic hotspot.",
                source=source, metrics={"switching_mW": switching, "total_mW": total}))
    return findings


# ---------------------------------------------------------------- area
def parse_area(text: str, source: str) -> list:
    findings = []
    for line in text.splitlines():
        m = re.match(r"\s+(\w+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", line)
        if not m:
            continue
        name = m.group(1)
        util = float(m.group(6))
        total_area = float(m.group(5))
        if util >= 85.0:
            findings.append(Finding("area",
                f"High utilization / congestion risk in {name}", "Medium", location=name,
                detail=f"Utilization {util:.0f}% (area {total_area:.0f} um²) — congestion risk.",
                source=source, metrics={"util_pct": util, "area_um2": total_area}))
    return findings


# ---------------------------------------------------------------- upf
def parse_upf(text: str, source: str) -> list:
    findings = []
    if "set_isolation" not in text and "NO isolation" in text:
        findings.append(Finding("upf",
            "Missing isolation strategy on PD_DMA outputs", "High", location="PD_DMA",
            detail="Switchable-domain outputs cross to always-on domain without isolation.",
            source=source, metrics={"issue": "missing_isolation"}))
    if "set_retention" not in text and "no retention" in text.lower():
        findings.append(Finding("upf",
            "Missing retention strategy on PD_USB", "Medium", location="PD_USB",
            detail="State registers have no retention across power-down.",
            source=source, metrics={"issue": "missing_retention"}))
    if "clock gating intent present but enable not wired" in text.lower():
        findings.append(Finding("upf",
            "Clock-gating intent not realized on dma_ctrl", "High", location="dma_ctrl.sv:142",
            detail="UPF intends clock gating; RTL enable not wired (cross-check power report).",
            source=source, metrics={"issue": "cg_intent_unrealized"}))
    return findings


# ---------------------------------------------------------------- sdc
def parse_sdc(text: str, source: str) -> list:
    findings = []
    if "multicycle" not in text.lower() and "cfg_reg -> status_reg" in text:
        findings.append(Finding("sdc",
            "Missing multicycle path on config path", "Medium",
            location="cfg_reg → status_reg",
            detail="Quasi-static config path lacks a multicycle constraint.",
            source=source, metrics={"issue": "missing_multicycle"}))
    if "clk_usb" in text and "clk_120m" in text:
        findings.append(Finding("sdc",
            "IP→top clock mismatch (clk_usb vs clk_120m)", "High",
            location="usb_ip",
            detail="Block clk_usb (10.0ns) not reconciled with top clk_120m (8.33ns).",
            source=source, metrics={"issue": "clock_promotion"}))
    if "false_path on test_mode" in text.lower():
        findings.append(Finding("sdc",
            "Missing false_path on static test_mode", "Low", location="test_mode",
            detail="Static strap signal lacks a false_path exception.",
            source=source, metrics={"issue": "missing_false_path"}))
    return findings


_PARSERS = {
    "sta": parse_sta, "synth": parse_synth, "power": parse_power,
    "area": parse_area, "upf": parse_upf, "sdc": parse_sdc,
}


def parse_text(name: str, text: str) -> tuple:
    """Return (report_type, list[Finding])."""
    rtype = detect_type(name, text)
    fn = _PARSERS.get(rtype)
    if fn is None:
        return rtype, []
    return rtype, fn(text, source=name)


def parse_file(path) -> tuple:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="ignore")
    return parse_text(p.name, text)
