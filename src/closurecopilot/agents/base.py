"""Base agent: RAG-grounded, LLM-optional enrichment around the fix-router."""
from __future__ import annotations

from ..models import Finding, Fix, AnalysisItem
from ..rag import get_kb
from .. import fix_router, llm


class SpecialistAgent:
    domain = "generic"
    name = "Specialist Agent"
    group = None
    reads: tuple = ()
    fix_layers: tuple = ()

    def __init__(self, domain=None, name=None, group=None,
                 reads=None, fix_layers=None) -> None:
        if domain is not None:
            self.domain = domain
        if name is not None:
            self.name = name
        if group is not None:
            self.group = group
        if reads is not None:
            self.reads = tuple(reads)
        if fix_layers is not None:
            self.fix_layers = tuple(fix_layers)

    def handles(self, f: Finding) -> bool:
        return f.domain == self.domain

    def analyze(self, f: Finding) -> AnalysisItem:
        fix: Fix = fix_router.route(f)
        kb = get_kb()
        query = f"{f.title} {f.detail} {f.domain} {fix.layer}"
        chunks = kb.retrieve(query)
        fix.references = [f"{c.store}:{c.title}" for c in chunks]

        # Optional LLM enrichment — grounded in RAG context. Offline -> keep rule rationale.
        grounding = "\n\n".join(f"[{c.store}] {c.title}\n{c.text}" for c in chunks)
        text = llm.chat(
            system=("You are a senior RTL/PPA closure engineer. Using ONLY the provided "
                    "knowledge, explain the issue and why the fix belongs in the stated "
                    "layer. Be concise (<=3 sentences). Do not invent constraints."),
            user=(f"ISSUE: {f.title}\nDETAIL: {f.detail}\nLOCATION: {f.location}\n"
                  f"PROPOSED LAYER: {fix.layer}\nRULE RATIONALE: {fix.rationale}\n\n"
                  f"KNOWLEDGE:\n{grounding}"),
        )
        if text:
            fix.rationale = text.strip()
        return AnalysisItem(finding=f, fix=fix)


class PowerAgent(SpecialistAgent):
    domain, name = "power", "Power Agent"


class TimingAgent(SpecialistAgent):
    domain, name = "timing", "Performance / Timing Agent"


class AreaAgent(SpecialistAgent):
    domain, name = "area", "Area Agent"


class SynthesisAgent(SpecialistAgent):
    domain, name = "synthesis", "Synthesis Agent"


class UPFAgent(SpecialistAgent):
    domain, name = "upf", "UPF (Power Intent) Agent"


class ConstraintsAgent(SpecialistAgent):
    domain, name = "sdc", "Constraints (SDC) Agent"
