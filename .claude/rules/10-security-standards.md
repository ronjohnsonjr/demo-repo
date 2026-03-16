# Security Standards

## Secrets Management
- **NEVER** commit tokens, passwords, or API keys to the repository.
- Use `config/config.json` (gitignored) or environment variables for secrets.
- Use `.env.example` as a template — never commit `.env`.
- Pre-commit hooks include `gitleaks` and `detect-private-key` to catch leaks.

## HTTP Security
- Never disable SSL verification (`verify=False`).
- Always use the `GitHubHTTPClient` which enforces HTTPS.
- Token is passed via `Authorization: Bearer` header, never in URLs.

## Code Scanning
- `bandit` scans `utils/`, `data/`, and `scripts/` for security issues.
- `semgrep` rules in `.semgrep.yml` catch hardcoded tokens and insecure patterns.
- `ruff` with `S` (bandit) rules enabled for inline security checks.
