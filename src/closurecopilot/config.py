"""Configuration + environment loading for ClosureCopilot."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # dotenv optional
    pass

# Repo paths (this file: src/closurecopilot/config.py)
PKG_DIR = Path(__file__).resolve().parent
SRC_DIR = PKG_DIR.parent
REPO_ROOT = SRC_DIR.parent
DATA_DIR = REPO_ROOT / "data"
SAMPLES_DIR = DATA_DIR / "samples"
KNOWLEDGE_GLOBAL = DATA_DIR / "knowledge" / "global"
KNOWLEDGE_DESIGN = DATA_DIR / "knowledge" / "design"


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


AZURE_ENDPOINT = _env("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = _env("AZURE_OPENAI_API_KEY")
AZURE_API_VERSION = _env("AZURE_OPENAI_API_VERSION", "2024-06-01")
AZURE_CHAT_DEPLOYMENT = _env("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")
AZURE_EMBED_DEPLOYMENT = _env("AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-small")

FORCE_OFFLINE = _env("CLOSURECOPILOT_OFFLINE", "0") == "1"


def is_online() -> bool:
    """True when Azure OpenAI is configured and offline mode is not forced."""
    return bool(AZURE_ENDPOINT and AZURE_API_KEY) and not FORCE_OFFLINE


def mode_label() -> str:
    return "azure-openai" if is_online() else "offline"
