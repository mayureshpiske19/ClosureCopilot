"""Declarative agent registry.

Loads the specialist agents from ``agents.yaml`` at the repo root so the roster
is data-driven — adding or re-tuning an agent is a config change, no code edit.
Falls back to a built-in default roster if the file or PyYAML is unavailable, so
the pipeline always runs offline.
"""
from __future__ import annotations

from .. import config
from .base import SpecialistAgent

# Built-in fallback — mirrors agents.yaml so the pipeline runs even without it.
_DEFAULTS = [
    {"domain": "synthesis", "name": "Synthesis Agent", "group": "collaterals",
     "reads": ["synthesis"], "fix_layers": ["Synth", "RTL"]},
    {"domain": "upf", "name": "UPF (Power Intent) Agent", "group": "collaterals",
     "reads": ["upf"], "fix_layers": ["UPF", "RTL"]},
    {"domain": "sdc", "name": "Constraints (SDC) Agent", "group": "collaterals",
     "reads": ["sdc"], "fix_layers": ["SDC"]},
    {"domain": "power", "name": "Power Agent", "group": "ppa",
     "reads": ["rtla", "sta"], "fix_layers": ["UPF", "RTL"]},
    {"domain": "timing", "name": "Performance / Timing Agent", "group": "ppa",
     "reads": ["sta"], "fix_layers": ["SDC", "RTL"]},
    {"domain": "area", "name": "Area Agent", "group": "ppa",
     "reads": ["synthesis", "rtla"], "fix_layers": ["RTL"]},
    {"domain": "formal", "name": "Formal (Equivalence) Agent", "group": "equivalence",
     "reads": ["lec"], "fix_layers": ["Formal", "RTL"]},
]


def load_specs(path=None) -> list[dict]:
    """Return the raw agent spec dicts from YAML, or the built-in defaults."""
    path = path or config.AGENTS_CONFIG
    try:
        import yaml  # optional dependency
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        specs = data.get("agents")
        if specs:
            return specs
    except Exception:
        pass
    return _DEFAULTS


def build_agents(path=None) -> list[SpecialistAgent]:
    """Instantiate specialist agents from the declarative registry."""
    return [
        SpecialistAgent(
            domain=s["domain"],
            name=s.get("name"),
            group=s.get("group"),
            reads=s.get("reads"),
            fix_layers=s.get("fix_layers"),
        )
        for s in load_specs(path)
    ]


ALL_AGENTS = build_agents()
