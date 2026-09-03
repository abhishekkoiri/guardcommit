# GuardCommit 🛡️
> **Blazing fast Git AI code reviewer, secret leak detector & conventional commit generator.**
> Stop pushing messy commit messages, broken diffs, and leaked API keys to production.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-10%20passed-brightgreen.svg)]()
[![Zero Heavy SDKs](https://img.shields.io/badge/dependencies-lightweight-purple.svg)]()
[![Supports Local LLMs](https://img.shields.io/badge/Ollama-100%25%20Free%20%26%20Offline-orange.svg)]()

---

## Why GuardCommit?

Most Git commit tools are either slow, require heavy 200MB SDKs, or only write generic one-line commit messages without checking if your code actually works or if you accidentally leaked an `.env` or OpenAI secret key.

**GuardCommit** is a zero-bloat, production-grade terminal tool built for modern developers:
1. **🛡️ Offline Secret Scanner:** Catches AWS, OpenAI, Stripe, GitHub tokens, and `.env` files *before* you push.
2. **🧠 AI Pre-Commit Code Reviewer:** Performs an automated senior-engineer code review on staged diffs to catch logic bugs and performance leaks.
3. **✨ Conventional Commit 1.0.0 Generator:** Analyzes unified git diffs and crafts clean semantic commit titles + bulleted summaries.
4. **🚀 Instant Pull Request Generator:** Compares branches against `main` and creates structured GitHub PR markdown ready to paste.
5. **⚡ Multi-Model & Local First:** Works with **Ollama** (100% local, completely free, zero data leaving your machine), **Groq** (sub-500ms lightning inference), **Google Gemini**, and **OpenAI/DeepSeek**.
6. **📊 Real-time Token & Sub-Cent Cost Tracking:** Displays exact tokens, latency, and costs directly in your terminal.

---

## 🚀 Quickstart (30 Seconds)

### 1. Install via pip
```bash
pip install guardcommit
```
*(Or clone this repo and run `pip install -e .`)*

### 2. Configure Your Provider
Run the interactive setup wizard:
```bash
guardcommit config
```
*Supports Groq (free), Ollama (free local), Gemini, or OpenAI.*

---

## 💻 Usage & Commands

### 1. Generate a Semantic Conventional Commit
Stage your changes, then run:
```bash
guardcommit commit
```
* **Interactive Terminal UI:** Displays 3 clean commit options conforming to Conventional Commits standard.
* **Auto-Blocks Leaks:** Automatically aborts commit if sensitive API credentials are detected in the diff!

### 2. Scan Staged Changes for Leaked Secrets
```bash
guardcommit scan
```
Detects:
* AWS Access Keys (`AKIA...`)
* OpenAI / Anthropic Secret Keys (`sk-proj-...`, `sk-ant-...`)
* GitHub Personal Access Tokens (`ghp_...`, `github_pat_...`)
* Stripe API Keys (`sk_live_...`)
* Private SSH/RSA Keys (Standard RSA / OpenSSH private key headers)
* Staged `.env`, `.env.local`, `credentials.json`, `*.pem` files.
* Shannon entropy randomness checks for suspicious secrets.

### 3. Run Pre-Commit AI Code Review
```bash
guardcommit review
```
Produces an actionable, markdown-rendered review report covering:
* Logic bugs & edge cases
* Security flaws (SQL injection, unsafe input)
* Async bottlenecks & unhandled exceptions

### 4. Generate a Full GitHub Pull Request
```bash
guardcommit pr --base main --output pr.md
```
Generates complete PR summaries, architectural impacts, and testing checklists comparing your branch against `main`.

### 5. Install Automated Git Pre-Commit Hook
Prevent anyone on your team from accidentally committing secrets:
```bash
guardcommit hook install
```
*Installs a lightweight hook into `.git/hooks/pre-commit`. Now, every `git commit` is automatically verified!*

To remove:
```bash
guardcommit hook uninstall
```

---

## ⚡ Supported LLM Providers

| Provider | Speed | Cost | Privacy |
| :--- | :--- | :--- | :--- |
| **Ollama** *(Llama 3, Qwen, Mistral)* | 🚀 Fast | **$0.00 (100% Free)** | 🔒 100% Local (Zero data leaves device) |
| **Groq** *(Qwen 27B / Llama 3)* | ⚡ Ultra-Fast (<500ms) | **Free tier available** | Cloud |
| **Google Gemini** *(2.5 Flash)* | 🚀 Very Fast | Sub-cent ($0.00004) | Cloud |
| **OpenAI / DeepSeek** | 🚀 Fast | Standard API rate | Cloud |

---

## 🧪 Testing & Verification

Run the comprehensive unit test suite:
```bash
pytest -v
```

---

## 🤝 Contributing & License

Contributions are welcome! Please feel free to open a Pull Request or Issue.
Licensed under the [MIT License](LICENSE).
