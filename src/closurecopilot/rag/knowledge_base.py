"""Dual-RAG knowledge layer.

Two stores:
  * GLOBAL  — PPA design principles, tool-report semantics, fix patterns (static).
  * DESIGN  — Design Context Memory: specs, micro-arch, past reports (per project, grows).

Retrieval is a dependency-free keyword/overlap scorer so it always runs. When Azure
OpenAI embeddings are configured you can swap in a vector store (Chroma) without changing
the agent-facing API (`retrieve`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .. import config


@dataclass
class Chunk:
    store: str          # "global" | "design"
    title: str          # heading / doc title
    text: str
    source: str         # file name


_STOP = set("the a an of to in on is are and or for with by as at be this that it its "
            "not no if then else when which per once so".split())


def _tokenize(s: str) -> set:
    return {w for w in re.findall(r"[a-z_][a-z0-9_]+", s.lower()) if w not in _STOP}


def _load_store(folder: Path, store: str) -> list:
    chunks = []
    if not folder.exists():
        return chunks
    for md in sorted(folder.glob("*.md")):
        text = md.read_text(encoding="utf-8", errors="ignore")
        # split into sections by markdown headings
        parts = re.split(r"\n(?=#{1,3}\s)", text)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            h = re.match(r"#{1,3}\s*(.+)", part)
            title = h.group(1).strip() if h else md.stem
            chunks.append(Chunk(store, title, part, md.name))
    return chunks


class KnowledgeBase:
    def __init__(self) -> None:
        self.global_chunks = _load_store(config.KNOWLEDGE_GLOBAL, "global")
        self.design_chunks = _load_store(config.KNOWLEDGE_DESIGN, "design")

    def _search(self, chunks: list, query: str, k: int) -> list:
        q = _tokenize(query)
        scored = []
        for c in chunks:
            overlap = len(q & _tokenize(c.text))
            if overlap:
                scored.append((overlap, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:k]]

    def retrieve(self, query: str, k_global: int = 2, k_design: int = 2) -> list:
        """Return grounding chunks from BOTH stores (design context first)."""
        return (self._search(self.design_chunks, query, k_design)
                + self._search(self.global_chunks, query, k_global))

    def stats(self) -> dict:
        return {"global_chunks": len(self.global_chunks),
                "design_chunks": len(self.design_chunks)}


_kb = None


def get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb
