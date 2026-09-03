"""
Configuration manager for GuardCommit.
Manages provider preferences, API keys, and local LLM endpoints (~/.guardcommit/config.json).
"""

from __future__ import annotations
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".guardcommit"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Config:
    default_provider: str = "groq"  # "groq", "ollama", "gemini", "openai"
    groq_api_key: Optional[str] = None
    groq_model: str = "qwen/qwen3.8-27b"
    ollama_endpoint: str = "http://localhost:11434"
    ollama_model: str = "llama3:latest"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    conventional_emoji: bool = True
    strict_secret_block: bool = True


def load_config() -> Config:
    """Load configuration from disk with environment variable fallbacks."""
    config_data = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            config_data = {}

    cfg = Config(**{k: v for k, v in config_data.items() if k in Config.__annotations__})

    # Environment variable overrides
    if os.getenv("GROQ_API_KEY"):
        cfg.groq_api_key = os.getenv("GROQ_API_KEY")
    if os.getenv("GEMINI_API_KEY"):
        cfg.gemini_api_key = os.getenv("GEMINI_API_KEY")
    if os.getenv("OPENAI_API_KEY"):
        cfg.openai_api_key = os.getenv("OPENAI_API_KEY")
    if os.getenv("OLLAMA_HOST"):
        cfg.ollama_endpoint = os.getenv("OLLAMA_HOST")
    if os.getenv("GUARDCOMMIT_PROVIDER"):
        cfg.default_provider = os.getenv("GUARDCOMMIT_PROVIDER")

    return cfg


def save_config(cfg: Config) -> None:
    """Save configuration to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(cfg), f, indent=2)
