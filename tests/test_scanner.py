import pytest
from guardcommit.scanner import (
    calculate_shannon_entropy,
    scan_file_paths,
    scan_diff_content,
    scan_staged_changes,
)


def test_restricted_file_detection():
    staged = [
        "src/app.py",
        ".env",
        ".env.local",
        "keys/id_rsa",
        "certs/server.pem",
        "config/secrets.json",
        "README.md",
    ]
    findings = scan_file_paths(staged)
    flagged_files = [f.file_path for f in findings]
    assert ".env" in flagged_files
    assert ".env.local" in flagged_files
    assert "keys/id_rsa" in flagged_files
    assert "certs/server.pem" in flagged_files
    assert "config/secrets.json" in flagged_files
    assert "src/app.py" not in flagged_files
    assert "README.md" not in flagged_files


def test_aws_key_detection():
    diff = """
--- a/config.py
+++ b/config.py
@@ -1,3 +1,4 @@
 import os
+AWS_KEY = "AKIAIOSFODNN7EXAMPL9"
"""
    findings = scan_diff_content(diff)
    assert len(findings) == 1
    assert findings[0].rule_name == "AWS Access Key ID"
    assert findings[0].severity == "CRITICAL"


def test_openai_key_detection():
    diff = """
--- a/ai.py
+++ b/ai.py
@@ -5,2 +5,3 @@
 def get_client():
+    token = "sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx"
     return token
"""
    findings = scan_diff_content(diff)
    assert any("OpenAI" in f.rule_name for f in findings)


def test_github_token_detection():
    diff = """
--- a/deploy.sh
+++ b/deploy.sh
@@ -1,2 +1,3 @@
 #!/bin/bash
+export GITHUB_TOKEN="ghp_1234567890abcdefghijklmnopqrstuvwxyz"
"""
    findings = scan_diff_content(diff)
    assert any("GitHub" in f.rule_name for f in findings)


def test_clean_diff_no_false_positives():
    diff = """
--- a/main.py
+++ b/main.py
@@ -10,3 +10,4 @@
 def calculate_total(items):
+    return sum(item.price for item in items)
"""
    findings = scan_diff_content(diff)
    assert len(findings) == 0


def test_shannon_entropy():
    low = "aaaaaaaaaaaaaaaaaaaa"
    assert calculate_shannon_entropy(low) == 0.0

    high = "xK9#mQ2$zL8*vP1@wR7!"
    assert calculate_shannon_entropy(high) > 4.0
