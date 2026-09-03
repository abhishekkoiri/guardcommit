"""
Provider factory with intelligent auto-discovery and fallbacks for GuardCommit.
"""

from __future__ import annotations
from typing import Optional
from guardcommit.config import Config, load_config
from guardcommit.providers.base import BaseLLMProvider
from guardcommit.providers.groq import GroqProvider
from guardcommit.providers.ollama import OllamaProvider
from guardcommit.providers.gemini import GeminiProvider
from guardcommit.providers.openai import OpenAIProvider


def get_provider(
    provider_name: Optional[str] = None,
    config: Optional[Config] = None
) -> BaseLLMProvider:
    """
    Instantiate the requested LLM provider or auto-detect available providers.
    Order of preference for auto-detect: Groq -> Gemini -> OpenAI -> Ollama.
    """
    cfg = config or load_config()
    target = (provider_name or cfg.default_provider).lower()

    if target == "groq":
        return GroqProvider(api_key=cfg.groq_api_key, model=cfg.groq_model)
    elif target == "ollama":
        return OllamaProvider(endpoint=cfg.ollama_endpoint, model=cfg.ollama_model)
    elif target == "gemini":
        return GeminiProvider(api_key=cfg.gemini_api_key, model=cfg.gemini_model)
    elif target in ("openai", "deepseek"):
        return OpenAIProvider(api_key=cfg.openai_api_key, model=cfg.openai_model)
    else:
        if cfg.groq_api_key:
            return GroqProvider(api_key=cfg.groq_api_key, model=cfg.groq_model)
        if cfg.gemini_api_key:
            return GeminiProvider(api_key=cfg.gemini_api_key, model=cfg.gemini_model)
        if cfg.openai_api_key:
            return OpenAIProvider(api_key=cfg.openai_api_key, model=cfg.openai_model)
        return OllamaProvider(endpoint=cfg.ollama_endpoint, model=cfg.ollama_model)
