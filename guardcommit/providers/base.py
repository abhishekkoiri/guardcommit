"""
Base LLM provider interface and response structures with token & cost tracking.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    estimated_cost_usd: float = 0.0
    provider_name: str = "unknown"
    model_name: str = "unknown"


class BaseLLMProvider(ABC):
    """Abstract interface for lightweight, zero-SDK LLM clients."""

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Synchronously generate completion for the given prompt."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider credentials or endpoint are configured."""
        pass
