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


# ---- product modules -----------------------------------------------------
from closurecopilot import config
from closurecopilot.modules import promotion, regression, physical, upf_signoff


def test_constraint_promotion_detects_mismatches():
    items = promotion.run_on_samples(config.SAMPLES_DIR)
    assert len(items) >= 3
    # clk_usb has no top match -> promotion finding routed to SDC
    assert any("clk_usb" in it.finding.title and it.fix.layer == LAYER_SDC for it in items)


def test_regression_attributes_to_commit():
    items = regression.run_on_samples(config.SAMPLES_DIR)
    pipe = [it for it in items if "pipe_stage3" in it.finding.location]
    assert pipe, "expected pipe_stage3 power regression"
    assert any("commit" in it.finding.metrics for it in pipe)


def test_physical_flags_congestion_hotspots():
    items = physical.run_on_samples(config.SAMPLES_DIR)
    assert any("crc_gen" in it.finding.location for it in items)
    assert all(it.fix.layer == LAYER_RTL for it in items)


def test_upf_signoff_checklist_has_failures():
    items = upf_signoff.run_on_samples(config.SAMPLES_DIR)
    rows = upf_signoff.checklist(items)
    assert len(rows) == 3
    assert any("FAIL" in status for _, status, _ in rows)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
    print("all tests passed")
