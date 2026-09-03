# GuardCommit 🛡️
> A fast, offline-first Git pre-commit hook that detects likely secrets before they reach Git history and uses AI to generate Conventional Commit messages and pull-request descriptions from staged diffs.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-10%20passed-brightgreen.svg)]()
[![Zero Heavy SDKs](https://img.shields.io/badge/dependencies-lightweight%20(httpx)-purple.svg)]()
[![Supports Local LLMs](https://img.shields.io/badge/Ollama-100%25%20Free%20%26%20Offline-orange.svg)]()

---

### The Three Pillars

* 🔒 **Blocks likely API keys, tokens, private keys, and `.env` files before commit** using offline regex rules and Shannon entropy algorithms.
* ✨ **Generates Conventional Commits and PR descriptions from staged diffs** with interactive terminal selection.
* 🦙 **Works locally with Ollama** (100% free & offline privacy) or through **Groq**, **Gemini**, and **OpenAI**.

---

## 💡 Why Not Just `.gitignore`?

`.gitignore` only ignores **entire files by name**. It is completely blind to secrets accidentally pasted inside legitimate source code files (`auth.py`, `config.ts`, `database.go`) that you *must* commit.

| Security Feature | `.gitignore` / `.dockerignore` | **GuardCommit** 🛡️ |
| :--- | :---: | :---: |
| **Blocks known filenames (`.env`, `id_rsa`)** | ✅ Yes (Only if manually added) | ✅ **Yes** (Built-in offline rules) |
| **Inspects code diffs for hardcoded API keys** | ❌ **No (Blind to contents)** | ✅ **Yes** (AWS, OpenAI, Stripe, GitHub, etc.) |
| **Detects high-entropy random secret tokens** | ❌ **No** | ✅ **Yes** (Shannon Entropy math) |
| **Generates Conventional Commit messages** | ❌ **No** | ✅ **Yes** (AI Conventional Commits 1.0.0) |
| **Generates Pull Request descriptions** | ❌ **No** | ✅ **Yes** |
| **Automated Git pre-commit protection** | ❌ **No** | ✅ **Yes** (`guardcommit hook install`) |

---

## ⚡ Live Terminal Flow

```text
# 1. When an API key or .env is accidentally staged:
$ git add .env
$ guardcommit commit
🚨 BLOCKED: 1 high-risk credential detected in staged diff!
┌──────────┬──────────────────────────────────┬─────────┬──────┬──────────────────┐
│ Severity │ Rule / Secret Type               │ File    │ Line │ Snippet (Masked) │
├──────────┼──────────────────────────────────┼─────────┼──────┼──────────────────┤
│ CRITICAL │ Restricted Environment File      │ .env    │ -    │ .env             │
└──────────┴──────────────────────────────────┴─────────┴──────┴──────────────────┘
⚠️ Commit aborted to protect your repository from credential leaks.

# 2. When your staged code is clean:
$ git add src/auth.py
$ guardcommit commit
✔ Security Audit Passed! (Zero sensitive keys detected)
⚡ Analyzing diff with Groq...

Select a Conventional Commit Title:
  [1] feat(auth): add OAuth2 session token validation utility
  [2] feat(auth): introduce HMAC-SHA256 signature verifier
  [3] refactor(auth): sanitize user payload before hashing
Choose an option [1]: 1
✔ Committed successfully! (420ms | Cost: $0.0003)
```

---

## 🚀 Quickstart (30 Seconds)

### 1. Install Directly via Git
```bash
pip install git+https://github.com/abhishekkoiri/guardcommit.git
```
*(Or clone this repo and run `pip install -e .`)*

### 2. Configure Your Preferred Provider
Run the interactive configuration wizard:
```bash
guardcommit config
```
* **Ollama (Default for Privacy):** 100% local, zero keys needed.
* **Groq (Default for Cloud):** Ultra-fast sub-500ms inference with free API key.
* **Google Gemini & OpenAI:** Standard cloud APIs with tiered model pricing.

### 3. Install Automated Pre-Commit Protection
Enable automated secret blocking across your repository:
```bash
guardcommit hook install
```
*Now, whenever you run `git commit`, GuardCommit automatically verifies staged changes before Git allows the commit!*

---

## 💻 CLI Command Reference

| Command | Description |
| :--- | :--- |
| `guardcommit scan` | Scan staged files & diff for leaked API keys, tokens, and `.env` files. |
| `guardcommit commit` | Scan diff for secrets, then generate Conventional Commit options. |
| `guardcommit review` | Perform an automated pre-commit AI code review on staged diffs. |
| `guardcommit pr --base main` | Compare current branch against base and output full GitHub PR markdown. |
| `guardcommit hook install` | Install automated Git pre-commit hook into `.git/hooks/pre-commit`. |
| `guardcommit hook uninstall` | Remove GuardCommit pre-commit hook. |
| `guardcommit config` | Configure default provider, model, and API keys. |

---

## ⚡ Supported Providers & Models

| Provider | Supported Models | Speed | Privacy & Cost |
| :--- | :--- | :--- | :--- |
| **Ollama** | `llama3.2`, `qwen2.5-coder`, `mistral` | 🚀 Fast | 🔒 100% Local (Free) |
| **Groq** | `qwen/qwen3.8-27b`, `openai/gpt-oss-20b` | ⚡ Ultra-Fast (<500ms) | Free Developer Tier |
| **Google Gemini** | `gemini-2.0-flash`, `gemini-3.1-flash-lite`, `gemini-2.5-pro` | 🚀 Very Fast | Sub-cent ($0.075 / 1M) |
| **OpenAI / DeepSeek** | `gpt-4o-mini`, `deepseek-chat` | 🚀 Fast | Standard API rate |

---

## 🧪 Testing & Verification

Run the automated test suite locally:
```bash
pytest -v
```

---

## 📄 Trust & Documentation
* [Security Policy & Responsible Disclosure](SECURITY.md)
* [Contributing Guidelines](CONTRIBUTING.md)
* [Changelog & Releases](CHANGELOG.md)
* [MIT License](LICENSE)
