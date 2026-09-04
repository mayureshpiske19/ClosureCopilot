"""Core data models shared across parsers, agents and the orchestrator."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Fix layers — the "where do I fix it?" routing decision.
LAYER_RTL = "RTL"
LAYER_SDC = "SDC (constraints)"
LAYER_UPF = "UPF (power intent)"
LAYER_SYNTH = "Synthesis setup"

SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


@dataclass
class Finding:
    """A single issue extracted from a backend report."""
    domain: str                       # timing | power | area | synthesis | upf | sdc
    title: str
    severity: str = "Medium"          # High | Medium | Low
    location: str = ""                # instance or file:line
    detail: str = ""
    metrics: dict = field(default_factory=dict)
    source: str = ""                  # report file it came from
    key: str = ""                     # stable id used to route/enrich

    def __post_init__(self) -> None:
        if not self.key:
            self.key = f"{self.domain}:{self.location or self.title}".lower()


@dataclass
class Fix:
    """A routed, actionable fix recommendation for a finding."""
    layer: str                        # LAYER_* — RTL / SDC / UPF / Synthesis
    rationale: str = ""
    snippet: str = ""                 # copy-paste-ready corrected code
    tradeoff: dict = field(default_factory=dict)  # {timing, power, area} deltas
    confidence: float = 0.8
    references: list = field(default_factory=list)  # RAG doc titles cited


@dataclass
class AnalysisItem:
    finding: Finding
    fix: Optional[Fix] = None

    @property
    def severity_rank(self) -> int:
        return SEVERITY_ORDER.get(self.finding.severity, 1)


@dataclass
class AnalysisResult:
    items: list = field(default_factory=list)   # list[AnalysisItem]
    summary: str = ""
    mode: str = "offline"                        # offline | azure-openai

    def ranked(self) -> list:
        return sorted(self.items, key=lambda it: it.severity_rank)

    def by_domain(self, domain: str) -> list:
        return [it for it in self.items if it.finding.domain == domain]
