# Contributing to GuardCommit 🤝

Thank you for your interest in contributing to GuardCommit! We welcome bug reports, new secret scanner regexes, provider integrations, and documentation improvements.

---

## Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/abhishekkoiri/guardcommit.git
cd guardcommit
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS / Linux:
source .venv/bin/activate
```

### 3. Install in editable mode with development dependencies
```bash
pip install -e .[dev]
```

---

## Running Tests

All contributions must pass the automated test suite before opening a Pull Request:

```bash
pytest -v
```

---

## Making Changes & Pull Requests

1. **Create a branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Follow Conventional Commits:**
   * `feat:` A new feature or provider.
   * `fix:` A bug fix or false-positive/negative scanner adjustment.
   * `docs:` Documentation improvements.
   * `test:` Adding or updating tests.
3. **Open a Pull Request:** Describe the problem your change solves and link any relevant issues.
