"""Supervisor / Orchestrator agent.

Ingests reports, dispatches each finding to the right specialist agent, cross-correlates
domains (PPA trade-off + intent-vs-measured), ranks issues, and produces a plain-language
closure summary. Runs fully offline; upgrades to Azure OpenAI phrasing when configured.
"""
from __future__ import annotations

from pathlib import Path

from . import config, llm
from .models import AnalysisResult
from .ingestion import parse_file, parse_text
from .agents import ALL_AGENTS
from .rag import get_kb


class Supervisor:
    def __init__(self) -> None:
        self.agents = ALL_AGENTS
        self.kb = get_kb()

    # -- ingestion -------------------------------------------------------
    def ingest_paths(self, paths) -> list:
        findings = []
        for p in paths:
            _, fs = parse_file(p)
            findings.extend(fs)
        return findings

    def ingest_texts(self, named_texts) -> list:
        findings = []
        for name, text in named_texts:
            _, fs = parse_text(name, text)
            findings.extend(fs)
        return findings

    # -- dispatch --------------------------------------------------------
    def _agent_for(self, f):
        for a in self.agents:
            if a.handles(f):
                return a
        return self.agents[0]

    def analyze(self, findings) -> AnalysisResult:
        items = []
        for f in findings:
            agent = self._agent_for(f)
            items.append(agent.analyze(f))
        result = AnalysisResult(items=items, mode=config.mode_label())
        result.summary = self._summarize(result)
        return result

    def run(self, paths) -> AnalysisResult:
        return self.analyze(self.ingest_paths(paths))

    # -- cross-domain correlation + summary ------------------------------
    def _correlations(self, result) -> list:
        notes = []
        power_hits = {it.finding.location for it in result.by_domain("power")}
        # Intent-vs-measured: UPF gating intent + measured high clock power.
        for it in result.items:
            if it.finding.metrics.get("issue") == "cg_intent_unrealized":
                notes.append("UPF intends clock gating on dma_ctrl and the power report "
                             "measures high clock power there → intent NOT realized; "
                             "single RTL fix (wire the enable) closes both.")
        if "crc_gen" in power_hits and any(
                it.finding.location == "crc_gen" for it in result.by_domain("area")):
            notes.append("crc_gen is both an area/congestion hotspot and a switching-power "
                         "hotspot → pipelining the XOR tree helps area AND power.")
        return notes

    def _summarize(self, result) -> str:
        n = len(result.items)
        highs = sum(1 for it in result.items if it.finding.severity == "High")
        by_layer = {}
        for it in result.items:
            if it.fix:
                by_layer[it.fix.layer] = by_layer.get(it.fix.layer, 0) + 1
        layer_str = ", ".join(f"{k}: {v}" for k, v in sorted(by_layer.items()))
        corr = self._correlations(result)

        base = (f"Analyzed {n} findings ({highs} high severity). "
                f"Fix routing → {layer_str}. ")
        if corr:
            base += "Cross-domain insights: " + " ".join(corr)

        text = llm.chat(
            system=("You are a senior silicon PPA-closure lead. Write a crisp 3-4 sentence "
                    "executive summary for an RTL designer. Emphasize where fixes belong "
                    "(RTL/SDC/UPF) and any cross-domain trade-offs. No fluff."),
            user=base,
        )
        return (text.strip() if text else base)


def run_on_samples() -> AnalysisResult:
    """Convenience: analyze all bundled sample reports."""
    paths = sorted(Path(config.SAMPLES_DIR).glob("*"))
    report_paths = [p for p in paths if p.suffix.lower() in
                    (".rpt", ".log", ".sdc", ".upf")]
    return Supervisor().run(report_paths)
