"""Module 4 — PPA Regression Detective.

Diffs two backend runs (power + STA), flags regressions, and attributes each to the
commit that last touched the affected block ("git-blame for PPA").
"""
from __future__ import annotations

import re
from pathlib import Path

from ..models import Finding, Fix, AnalysisItem, LAYER_RTL, LAYER_SDC


def _power_rows(text: str) -> dict:
    rows = {}
    for line in text.splitlines():
        m = re.match(r"\s+(\w+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", line)
        if m:
            rows[m.group(1)] = {"internal": float(m.group(2)), "switching": float(m.group(3)),
                                "leakage": float(m.group(4)), "clock": float(m.group(5)),
                                "total": float(m.group(6))}
    return rows


def _wns_rows(text: str) -> dict:
    rows = {}
    for line in text.splitlines():
        m = re.match(r"\s*(clk_\w+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\d+)", line)
        if m:
            rows[m.group(1)] = {"wns": float(m.group(2)), "tns": float(m.group(3)),
                                "fail": int(m.group(4))}
    return rows


def _commits(csv_path) -> dict:
    out = {}
    p = Path(csv_path)
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^(\S+)\s+(\S+)\s+(\S+)\s+"?(.*?)"?$', line)
        if m:
            out[m.group(1)] = {"commit": m.group(2), "author": m.group(3),
                               "subject": m.group(4)}
    return out


def diff(power_base: str, power_new: str, sta_base: str, sta_new: str,
         commits: dict) -> list:
    items = []

    # ---- power regressions (per block) ----
    pb, pn = _power_rows(power_base), _power_rows(power_new)
    for blk, newv in pn.items():
        if blk == "soc_top" or blk not in pb:
            continue
        dt = newv["total"] - pb[blk]["total"]
        if dt > 0.3:  # mW regression threshold
            c = commits.get(blk)
            attrib = (f" Attributed to commit {c['commit']} by {c['author']}: "
                      f"\"{c['subject']}\"." if c else "")
            sev = "High" if dt >= 1.0 else "Medium"
            # which component moved most
            comp = max(("switching", "internal", "clock", "leakage"),
                       key=lambda k: newv[k] - pb[blk][k])
            f = Finding("regression",
                f"Power regression in {blk}: +{dt:.2f} mW", sev, location=blk,
                detail=f"Total power {pb[blk]['total']:.2f} → {newv['total']:.2f} mW "
                       f"(+{dt:.2f}). Largest mover: {comp} "
                       f"({pb[blk][comp]:.2f} → {newv[comp]:.2f} mW).{attrib}",
                metrics={"delta_mW": round(dt, 2), "component": comp,
                         **({"commit": c["commit"]} if c else {})},
                source="power_new.rpt")
            fx = Fix(LAYER_RTL,
                rationale=f"The {comp} power rose after the attributed change — review that "
                          f"commit's RTL edit to {blk} (e.g. dropped pipeline stage / wider "
                          f"datapath increases toggling).",
                snippet=f"# git show {c['commit']} -- {blk}   # inspect the regressing change"
                        if c else f"# inspect recent RTL changes to {blk}",
                tradeoff={"power": f"recover ~{dt:.1f} mW", "timing": "check", "area": "check"},
                confidence=0.8)
            items.append(AnalysisItem(f, fx))

    # ---- timing regressions (per clock) ----
    sb, sn = _wns_rows(sta_base), _wns_rows(sta_new)
    for clk, newv in sn.items():
        if clk not in sb:
            continue
        dwns = newv["wns"] - sb[clk]["wns"]   # more negative = worse
        if dwns < -0.05:
            sev = "High" if dwns <= -0.15 else "Medium"
            f = Finding("regression",
                f"Timing regression on {clk}: WNS {sb[clk]['wns']:.3f} → {newv['wns']:.3f} ns",
                sev, location=clk,
                detail=f"WNS worsened by {dwns:.3f} ns; failing endpoints "
                       f"{sb[clk]['fail']} → {newv['fail']}. Cross-check same-commit RTL edits.",
                metrics={"delta_wns_ns": round(dwns, 3)}, source="sta_new.rpt")
            fx = Fix(LAYER_RTL,
                rationale="WNS degraded between runs on this clock — bisect to the commit that "
                          "touched the worst path's block; if the path is quasi-static, the fix "
                          "may be an SDC exception instead.",
                snippet="# git bisect between baseline and new run for this clock's worst path",
                tradeoff={"timing": f"recover {abs(dwns):.3f} ns", "power": "check", "area": "check"},
                confidence=0.7)
            items.append(AnalysisItem(f, fx))
    return items


def run_on_samples(samples_dir) -> list:
    r = Path(samples_dir) / "runs"
    read = lambda n: (r / n).read_text(encoding="utf-8", errors="ignore")
    return diff(read("power_baseline.rpt"), read("power_new.rpt"),
                read("sta_baseline.rpt"), read("sta_new.rpt"),
                _commits(r / "commits.csv"))
