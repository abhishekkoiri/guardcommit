"""
Lightweight Gemini API client using pure httpx with exact official pricing for all Gemini 2.x and 3.x models.
"""

from __future__ import annotations
import time
from typing import Optional
import httpx
from guardcommit.providers.base import BaseLLMProvider, LLMResponse

# Exact official pricing per 1M tokens (USD)
GEMINI_MODEL_PRICING = {
    # 3.1 Generation
    "gemini-3.1-pro-preview": {"input": 2.00, "output": 12.00},
    "gemini-3.1-pro": {"input": 2.00, "output": 12.00},
    "gemini-3.1-flash-lite": {"input": 0.25, "output": 1.50},
    # 2.5 Generation
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    # 2.0 / 1.5 Generation
    "gemini-2.0-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.0-flash-lite": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
}


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str], model: str = "gemini-2.0-flash"):
        clean_model = model[7:] if model.startswith("models/") else model
        super().__init__(model=clean_model)
        self.api_key = api_key

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def _get_model_rates(self) -> dict:
        """Lookup exact model pricing with intelligent tier fallback."""
        model_key = self.model.lower().strip()
        if model_key in GEMINI_MODEL_PRICING:
            return GEMINI_MODEL_PRICING[model_key]

        # Heuristic fallback for custom or preview model variants
        if "3.1" in model_key and "pro" in model_key:
            return {"input": 2.00, "output": 12.00}
        elif "2.5" in model_key and "pro" in model_key:
            return {"input": 1.25, "output": 10.00}
        elif "pro" in model_key:
            return {"input": 1.25, "output": 10.00}
        elif "3.1" in model_key and "lite" in model_key:
            return {"input": 0.25, "output": 1.50}
        elif "2.5" in model_key and "lite" in model_key:
            return {"input": 0.10, "output": 0.40}
        elif "lite" in model_key:
            return {"input": 0.10, "output": 0.40}
        else:
            return {"input": 0.075, "output": 0.30}

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate exact cost down to fractions of a cent ($USD)."""
        rates = self._get_model_rates()
        cost = (prompt_tokens * rates["input"] + completion_tokens * rates["output"]) / 1_000_000.0
        return round(cost, 6)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if not self.api_key:
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY environment variable or run 'guardcommit config'.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"[System Instructions]: {system_prompt}"}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Understood. I will strictly follow these instructions."}]
            })

        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
            }
        }

        start = time.perf_counter()
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        candidates = data.get("candidates", [])
        content = ""
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts:
                content = parts[0].get("text", "").strip()

        usage = data.get("usageMetadata", {})
        prompt_tokens = usage.get("promptTokenCount", 0)
        completion_tokens = usage.get("candidatesTokenCount", 0)
        total_tokens = prompt_tokens + completion_tokens

        cost = self._calculate_cost(prompt_tokens, completion_tokens)

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=round(elapsed_ms, 2),
            estimated_cost_usd=cost,
            provider_name="Google Gemini",
            model_name=self.model,
        )
