"""Smoke tests for the ClosureCopilot pipeline (offline, deterministic)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ["CLOSURECOPILOT_OFFLINE"] = "1"

from closurecopilot.orchestrator import run_on_samples
from closurecopilot.models import LAYER_RTL, LAYER_SDC, LAYER_UPF


def test_pipeline_produces_findings():
    r = run_on_samples()
    assert len(r.items) >= 10
    assert r.mode == "offline"


def test_all_findings_are_routed():
    r = run_on_samples()
    for it in r.items:
        assert it.fix is not None
        assert it.fix.layer  # non-empty


def test_config_path_routes_to_sdc_not_rtl():
    # The quasi-static cfg_reg -> status_reg path must be fixed in constraints, not RTL.
    r = run_on_samples()
    cfg = [it for it in r.items
           if "clk_cfg" in it.finding.title or "cfg_reg" in it.finding.location]
    assert cfg, "expected the config timing path finding"
    assert any(it.fix.layer == LAYER_SDC for it in cfg)


def test_deep_cone_routes_to_rtl():
    r = run_on_samples()
    alu = [it for it in r.items if "alu.sv" in it.finding.location]
    assert alu and any(it.fix.layer == LAYER_RTL for it in alu)


def test_upf_isolation_routes_to_upf():
    r = run_on_samples()
    iso = [it for it in r.items if "isolation" in it.finding.title.lower()]
    assert iso and any(it.fix.layer == LAYER_UPF for it in iso)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
    print("all tests passed")
