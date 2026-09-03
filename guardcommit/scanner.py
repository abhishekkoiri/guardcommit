"""
High-speed offline secret and credential leak scanner for git diffs.
Detects sensitive tokens, API keys, private keys, and restricted file types.
"""

from __future__ import annotations
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class SecretFinding:
    rule_name: str
    file_path: str
    line_number: Optional[int]
    matched_snippet: str
    severity: str  # HIGH, CRITICAL, MEDIUM


# Dangerous file patterns that should never be committed
RESTRICTED_FILE_PATTERNS = [
    re.compile(r"^\.env($|\..*)", re.IGNORECASE),
    re.compile(r"^id_rsa(\.pub)?$", re.IGNORECASE),
    re.compile(r".*\.(pem|pkcs12|pfx|key|keystore)$", re.IGNORECASE),
    re.compile(r"^credentials\.json$", re.IGNORECASE),
    re.compile(r"^secrets\.(yaml|yml|json)$", re.IGNORECASE),
]

# High-risk secret patterns
SECRET_REGEX_RULES = [
    (
        "AWS Access Key ID",
        "CRITICAL",
        re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b")
    ),
    (
        "OpenAI / Anthropic Secret Key",
        "CRITICAL",
        re.compile(r"\b(sk-[a-zA-Z0-9_-]{24,}|sk-proj-[a-zA-Z0-9_-]{24,}|sk-ant-[a-zA-Z0-9_-]{24,})\b")
    ),
    (
        "GitHub Access Token",
        "CRITICAL",
        re.compile(r"\b(ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{60,82})\b")
    ),
    (
        "Stripe Live API Key",
        "CRITICAL",
        re.compile(r"\b(sk_live_[0-9a-zA-Z]{24,34})\b")
    ),
    (
        "Slack Bot/User Token",
        "HIGH",
        re.compile(r"\b(xox[baprs]-[0-9a-zA-Z-]{10,48})\b")
    ),
    (
        "Private RSA / SSH Key Block",
        "CRITICAL",
        re.compile(r"-----BEGIN (RSA|OPENSSH|EC|DSA|PGP|ENCRYPTED)? PRIVATE KEY-----")
    ),
    (
        "Generic Bearer / Basic Secret Token",
        "MEDIUM",
        re.compile(r"""(?i)(?:api_key|apikey|secret_key|auth_token|client_secret)[\s]*[=:]+[\s]*["']([a-zA-Z0-9_=-]{16,64})["']""")
    ),
]


def calculate_shannon_entropy(data: str) -> float:
    """Calculate Shannon entropy to identify high-randomness secret hashes."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    for char in set(data):
        prob = data.count(char) / length
        entropy -= prob * math.log2(prob)
    return entropy


def scan_file_paths(staged_files: List[str]) -> List[SecretFinding]:
    """Check if any staged filenames match dangerous sensitive patterns (.env, keys)."""
    findings: List[SecretFinding] = []
    for f in staged_files:
        name = Path(f).name
        for pattern in RESTRICTED_FILE_PATTERNS:
            if pattern.search(name):
                findings.append(
                    SecretFinding(
                        rule_name="Restricted Environment/Secret File",
                        file_path=f,
                        line_number=None,
                        matched_snippet=f"Staged file matches restricted pattern: {name}",
                        severity="CRITICAL",
                    )
                )
                break
    return findings


def scan_diff_content(diff_text: str, ignore_tests: bool = True) -> List[SecretFinding]:
    """
    Parse unified diff lines (specifically additions starting with '+')
    and scan for secrets and high-entropy strings.
    """
    findings: List[SecretFinding] = []
    current_file = "unknown"
    current_line = 0

    for raw_line in diff_text.splitlines():
        # Track file name in diff header
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:].strip()
            continue
        elif raw_line.startswith("@@"):
            # Extract line number from hunk header: @@ -1,5 +10,6 @@
            m = re.search(r"\+(\d+)", raw_line)
            if m:
                current_line = int(m.group(1))
            continue

        # Only scan added lines (+) and skip diff metadata (+++)
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            content = raw_line[1:].strip()
            current_line += 1

            if not content:
                continue

            # Skip test files and mock fixtures if ignore_tests is True
            if ignore_tests and (
                current_file.startswith("tests/")
                or "/tests/" in current_file
                or current_file.startswith("test_")
                or "EXAMPLE" in content
                or "# pragma: allowlist secret" in content
            ):
                continue

            # Run regex rule checks
            for rule_name, severity, regex in SECRET_REGEX_RULES:
                match = regex.search(content)
                if match:
                    val = match.group(0)
                    masked = val[:4] + "*" * (len(val) - 8) + val[-4:] if len(val) > 8 else "****"
                    findings.append(
                        SecretFinding(
                            rule_name=rule_name,
                            file_path=current_file,
                            line_number=current_line,
                            matched_snippet=f"... {masked} ...",
                            severity=severity,
                        )
                    )

            # High entropy heuristic for standalone tokens (length > 20, entropy > 4.5)
            tokens = re.findall(r"[A-Za-z0-9+/=_-]{24,}", content)
            for token in tokens:
                # Exclude common false positives (hashes in lockfiles, long words, urls)
                if token.startswith("http") or "/" in token or ".js" in token or ".py" in token:
                    continue
                if calculate_shannon_entropy(token) > 4.5:
                    masked = token[:4] + "..." + token[-4:]
                    # Check if already caught by a regex rule to prevent duplicate reporting
                    already_caught = any(f.line_number == current_line for f in findings)
                    if not already_caught:
                        findings.append(
                            SecretFinding(
                                rule_name="High Entropy Suspicious Token",
                                file_path=current_file,
                                line_number=current_line,
                                matched_snippet=f"Detected high entropy token: {masked}",
                                severity="HIGH",
                            )
                        )
        elif not raw_line.startswith("-"):
            current_line += 1

    return findings


def scan_staged_changes(staged_files: List[str], diff_text: str) -> List[SecretFinding]:
    """Unified scan of both staged filenames and the diff content."""
    findings = scan_file_paths(staged_files)
    findings.extend(scan_diff_content(diff_text))
    return findings
