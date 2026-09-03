"""
Conventional commit and PR markdown generator engine for GuardCommit.
"""

from __future__ import annotations
import json
import re
from typing import List, Tuple
from guardcommit.providers.base import BaseLLMProvider, LLMResponse

COMMIT_SYSTEM_PROMPT = """You are an expert software engineer and git master.
Your task is to analyze a unified git diff and generate 3 high-quality Conventional Commit options following the Conventional Commits 1.0.0 standard:
Format: <type>(<optional scope>): <description>

Allowed types:
- feat: A new feature
- fix: A bug fix
- refactor: A code change that neither fixes a bug nor adds a feature
- perf: A code change that improves performance
- test: Adding missing tests or correcting existing tests
- docs: Documentation only changes
- chore: Build process, tooling, dependencies, or auxiliary tool changes

Rules:
1. Imperative mood in description ("add feature", not "added" or "adding").
2. Under 72 characters for the title.
3. Do not capitalize the first word after the colon.
4. No trailing period.

You must respond with ONLY valid JSON with this schema:
{
  "options": [
    "feat(auth): add google oauth2 login provider",
    "fix(scanner): correct line number calculation in diff hunk",
    "refactor(cli): simplify command options"
  ],
  "body": "- Added support for google oauth2\\n- Updated user profile schema\\n- Handled callback error redirect"
}
"""

PR_SYSTEM_PROMPT = """You are an expert tech lead and software engineer.
Generate a comprehensive GitHub Pull Request description in markdown format based on the git diff.
Include:
- ## Summary of Changes
- ## Type of Change (Bug fix, New feature, Breaking change, Refactoring)
- ## Key Modifications (bullet points per component)
- ## Verification & Testing Checklist
- ## Potential Breaking Changes or Risks

Output clean, formatted markdown directly without meta commentary."""


def generate_commit_options(diff: str, provider: BaseLLMProvider) -> Tuple[List[str], str, LLMResponse]:
    """Generate 3 conventional commit title options and an optional body from staged diff."""
    truncated_diff = diff[:12000] if len(diff) > 12000 else diff
    prompt = f"Analyze this staged git diff and generate the JSON commit suggestions:\n\n```diff\n{truncated_diff}\n```"

    response = provider.generate(prompt=prompt, system_prompt=COMMIT_SYSTEM_PROMPT)
    raw = response.content.strip()

    cleaned = re.sub(r"^```(?:json)?\n?", "", raw, flags=re.MULTILINE)
    cleaned = re.sub(r"\n?```$", "", cleaned, flags=re.MULTILINE).strip()

    options = []
    body = ""
    try:
        data = json.loads(cleaned)
        options = data.get("options", [])
        body = data.get("body", "")
    except Exception:
        for line in raw.splitlines():
            line = line.strip().strip('"').strip("'").strip("-").strip()
            if any(line.startswith(prefix) for prefix in ["feat", "fix", "refactor", "perf", "test", "docs", "chore"]):
                options.append(line)
        if not options:
            options = ["chore: update codebase with staged changes"]

    return options[:3], body, response


def generate_pull_request(diff: str, base_branch: str, provider: BaseLLMProvider) -> Tuple[str, LLMResponse]:
    """Generate complete GitHub Pull Request markdown from branch diff against base."""
    truncated_diff = diff[:15000] if len(diff) > 15000 else diff
    prompt = f"Base Branch: {base_branch}\nGenerate a complete PR description for the following changes:\n\n```diff\n{truncated_diff}\n```"

    response = provider.generate(prompt=prompt, system_prompt=PR_SYSTEM_PROMPT)
    return response.content.strip(), response
