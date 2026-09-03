"""
Lightweight local Ollama inference client using pure httpx.
"""

from __future__ import annotations
import time
from typing import Optional
import httpx
from guardcommit.providers.base import BaseLLMProvider, LLMResponse


class OllamaProvider(BaseLLMProvider):
    def __init__(self, endpoint: str = "http://localhost:11434", model: str = "llama3:latest"):
        super().__init__(model=model)
        self.endpoint = endpoint.rstrip("/")

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(f"{self.endpoint}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2,
            }
        }

        start = time.perf_counter()
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{self.endpoint}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        content = data.get("message", {}).get("content", "").strip()
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)
        total_tokens = prompt_tokens + completion_tokens

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=round(elapsed_ms, 2),
            estimated_cost_usd=0.0,
            provider_name="Ollama (Local)",
            model_name=self.model,
        )
