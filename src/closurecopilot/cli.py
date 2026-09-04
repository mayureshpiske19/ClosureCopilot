"""Command-line runner (no UI) — useful for the demo video backup and CI.

Usage:
    python -m closurecopilot.cli                 # analyze bundled samples
    python -m closurecopilot.cli path\\to\\*.rpt   # analyze given reports
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import config
from .orchestrator import Supervisor, run_on_samples


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        paths = [Path(a) for a in argv]
        result = Supervisor().run(paths)
    else:
        result = run_on_samples()

    print(f"\nClosureCopilot — engine: {result.mode}")
    print("=" * 78)
    print(result.summary)
    print("=" * 78)
    for it in result.ranked():
        f, fx = it.finding, it.fix
        print(f"\n[{f.severity}] ({f.domain}) {f.title}")
        print(f"   location : {f.location or '-'}")
        print(f"   FIX IN   : {fx.layer}  (confidence {fx.confidence:.0%})")
        print(f"   why      : {fx.rationale}")
        if fx.snippet:
            for line in fx.snippet.splitlines():
                print(f"      | {line}")
        if fx.tradeoff:
            print("   trade-off: " + ", ".join(f"{k}={v}" for k, v in fx.tradeoff.items()))
    print(f"\nTotal: {len(result.items)} findings.  Config mode: {config.mode_label()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
