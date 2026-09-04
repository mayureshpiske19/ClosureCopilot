"""LLM access layer: Azure OpenAI when configured, deterministic offline otherwise.

Every agent calls `chat()` for natural-language explanation. In offline mode `chat()`
returns None and the agent falls back to its deterministic, rule-based rationale — so the
whole pipeline runs (and demos) with zero credentials.
"""
from __future__ import annotations

from typing import Optional

from . import config

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not config.is_online():
        return None
    try:
        from openai import AzureOpenAI
        _client = AzureOpenAI(
            azure_endpoint=config.AZURE_ENDPOINT,
            api_key=config.AZURE_API_KEY,
            api_version=config.AZURE_API_VERSION,
        )
        return _client
    except Exception:
        return None


def chat(system: str, user: str, temperature: float = 0.2) -> Optional[str]:
    """Return an LLM completion, or None in offline mode / on error."""
    client = _get_client()
    if client is None:
        return None
    try:
        resp = client.chat.completions.create(
            model=config.AZURE_CHAT_DEPLOYMENT,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content
    except Exception:
        return None
