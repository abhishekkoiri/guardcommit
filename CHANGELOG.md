# Changelog 📝

All notable changes to **GuardCommit** will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-09-03

### Added
- **Offline Secret Scanner (`scan`):** Fast regex and Shannon entropy algorithms to detect AWS keys, OpenAI/Anthropic keys, Stripe secrets, GitHub tokens, and restricted files (`.env`, `*.pem`, `id_rsa`).
- **AI Conventional Commit Generator (`commit`):** Generates 3 semantic Conventional Commit titles (1.0.0) with optional bulleted summary bodies directly from staged diffs.
- **AI Pull Request Generator (`pr`):** Compares branch against base branch (`main`) and outputs structured GitHub PR Markdown.
- **AI Pre-Commit Reviewer (`review`):** Lightweight AST and heuristic pre-commit code review report.
- **Zero-Heavy-SDK Multi-Provider Engine:** Pure `httpx` adapters for **Ollama** (100% local/offline), **Groq** (<500ms inference), **Google Gemini** (with tiered Lite/Flash/Pro pricing), and **OpenAI/DeepSeek**.
- **Automated Pre-Commit Git Hook (`hook install` / `hook uninstall`):** 1-click installer for `.git/hooks/pre-commit` to prevent accidental credential pushes.
- **Interactive Configuration Wizard (`config`):** Quick terminal CLI to configure provider preferences and API keys.
- **GitHub Actions CI Pipeline:** Automated multi-version testing matrix for Python 3.9, 3.10, 3.11, and 3.12.
