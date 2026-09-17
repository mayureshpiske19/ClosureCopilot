"""Export all ClosureCopilot analysis results to JSON for the HTML dashboard."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
os.environ["CLOSURECOPILOT_OFFLINE"] = "1"

from closurecopilot import config
from closurecopilot.orchestrator import Supervisor, run_on_samples
from closurecopilot.modules import promotion, regression, physical, upf_signoff


def item_to_dict(it):
    f, fx = it.finding, it.fix
    return {
        "domain": f.domain, "title": f.title, "severity": f.severity,
        "location": f.location, "detail": f.detail, "metrics": f.metrics,
        "source": f.source,
        "fix": None if not fx else {
            "layer": fx.layer, "rationale": fx.rationale, "snippet": fx.snippet,
            "tradeoff": fx.tradeoff, "confidence": fx.confidence,
            "references": fx.references,
        },
    }


ppa = run_on_samples()
S = config.SAMPLES_DIR
mods = {
    "promotion": promotion.run_on_samples(S),
    "upf": upf_signoff.run_on_samples(S),
    "regression": regression.run_on_samples(S),
    "physical": physical.run_on_samples(S),
}
sup = Supervisor()

data = {
    "mode": ppa.mode,
    "summary": ppa.summary,
    "correlations": sup._correlations(ppa),
    "ppa": [item_to_dict(it) for it in ppa.ranked()],
    "modules": {k: [item_to_dict(it) for it in v] for k, v in mods.items()},
    "upf_checklist": [
        {"label": lbl, "status": st, "note": note}
        for lbl, st, note in upf_signoff.checklist(mods["upf"])
    ],
    "kb": sup.kb.stats(),
}

out = os.path.join(os.path.dirname(__file__), "results.json")
json.dump(data, open(out, "w", encoding="utf-8"), indent=2)
print("wrote", out)
print("ppa findings:", len(data["ppa"]),
      "| modules:", {k: len(v) for k, v in data["modules"].items()})
