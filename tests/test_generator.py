import json
from guardcommit.generator import generate_commit_options
from guardcommit.providers.base import BaseLLMProvider, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    def __init__(self, mock_response: str):
        super().__init__(model="mock-model")
        self.mock_response = mock_response

    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, system_prompt: str = None) -> LLMResponse:
        return LLMResponse(
            content=self.mock_response,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=120.0,
            estimated_cost_usd=0.0001,
            provider_name="MockProvider",
            model_name=self.model,
        )


def test_generate_commit_options_valid_json():
    mock_json = json.dumps({
        "options": [
            "feat(auth): implement oauth login flow",
            "refactor(db): migrate connection pooling",
            "fix(api): handle missing user payload"
        ],
        "body": "- Added oauth provider\n- Updated migrations"
    })
    provider = MockLLMProvider(mock_json)
    options, body, stats = generate_commit_options("mock diff", provider)

    assert len(options) == 3
    assert options[0] == "feat(auth): implement oauth login flow"
    assert "Added oauth provider" in body
    assert stats.total_tokens == 150
    assert stats.latency_ms == 120.0


def test_generate_commit_options_markdown_fences():
    mock_json = """```json
{
  "options": [
    "feat(search): add fuzzy search matching"
  ],
  "body": "- implemented levenshtein distance"
}
```"""
    provider = MockLLMProvider(mock_json)
    options, body, stats = generate_commit_options("mock diff", provider)

    assert len(options) == 1
    assert options[0] == "feat(search): add fuzzy search matching"
