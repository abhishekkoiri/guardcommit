# Security Policy 🛡️

We take the security of **GuardCommit** seriously. Because GuardCommit operates as a pre-commit security filter designed to prevent credential leaks, we welcome and appreciate responsible disclosure of security vulnerabilities, secret detection bypasses, and edge cases.

## Supported Versions

| Version | Supported |
| :--- | :--- |
| `v0.1.x` | ✅ Yes |
| `< 0.1.0` | ❌ No |

---

## Reporting a Vulnerability

If you discover a security vulnerability (such as a false-negative secret bypass, unsafe subshell execution, or prompt-injection edge case), please **do not open a public GitHub issue**.

Instead, report it directly to the core maintainer:
* **Email:** [abhishekkoiri.ak@gmail.com](mailto:abhishekkoiri.ak@gmail.com)
* **Subject Line:** `[SECURITY] Vulnerability Report in GuardCommit`

### Please Include:
1. A clear description of the vulnerability or secret pattern bypass.
2. Steps to reproduce or a minimal git diff example.
3. Potential impact and any recommended remediation steps.

---

## Response Timeline

* **Acknowledgment:** Within 48 hours.
* **Triage & Validation:** Within 5 business days.
* **Patch Release & Advisory:** Coordinated release with contributor credit.
