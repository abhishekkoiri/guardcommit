"""
AI Code Reviewer and diff risk analyzer for GuardCommit.
"""

from __future__ import annotations
from typing import Tuple
from guardcommit.providers.base import BaseLLMProvider, LLMResponse

REVIEW_SYSTEM_PROMPT = """You are a Principal Software Engineer performing a rigorous pre-commit code review.
Analyze the provided git diff and produce an actionable, concise review report in GitHub-flavored Markdown.

Focus on:
1. **Critical Bugs & Logic Errors** (null dereference, unhandled exceptions, race conditions, edge cases)
2. **Security Vulnerabilities** (injection, insecure defaults, sanitization issues)
3. **Performance & Resource Leaks** (unindexed queries, unclosed connections, blocking loops in async code)
4. **Code Quality & Architecture** (naming clarity, dead code, test coverage suggestions)

Format:
### 🛡️ Code Review Findings
- **[CRITICAL / HIGH / MEDIUM / LOW]** `filename:line`: Brief explanation & recommended fix.

### 💡 Recommendation
- A 1-2 sentence final verdict (e.g. "Safe to merge", "Fix critical issues before committing").

If the code is clean and has no concerns, reply with:
"### ✅ Code Quality Check: PASSED\\nNo bugs, security vulnerabilities, or performance bottlenecks identified in staged changes."
Keep the tone constructive and direct. Avoid unnecessary conversational filler."""


def review_staged_code(diff: str, provider: BaseLLMProvider) -> Tuple[str, LLMResponse]:
    """Run an AI code review on the staged git diff."""
    truncated_diff = diff[:15000] if len(diff) > 15000 else diff
    prompt = f"Review the following staged git diff:\n\n```diff\n{truncated_diff}\n```"

    response = provider.generate(prompt=prompt, system_prompt=REVIEW_SYSTEM_PROMPT)
    return response.content.strip(), response
