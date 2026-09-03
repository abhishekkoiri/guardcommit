"""
Lightweight Groq inference client using pure httpx.
"""

from __future__ import annotations
import time
from typing import Optional
import httpx
from guardcommit.providers.base import BaseLLMProvider, LLMResponse


class GroqProvider(BaseLLMProvider):
    ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: Optional[str], model: str = "qwen/qwen3.8-27b"):
        super().__init__(model=model)
        self.api_key = api_key

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("gsk_"))

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if not self.api_key:
            raise ValueError("Groq API key not configured. Set GROQ_API_KEY environment variable or run 'guardcommit config'.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        start = time.perf_counter()
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self.ENDPOINT, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        content = data["choices"][0]["message"]["content"].strip()
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        cost = (prompt_tokens * 0.59 + completion_tokens * 0.79) / 1_000_000.0

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=round(elapsed_ms, 2),
            estimated_cost_usd=round(cost, 6),
            provider_name="Groq",
            model_name=self.model,
        )
