# GitHub API Automation — Claude Code Instructions

## Project Overview
- This repo drives GitHub REST API tests with `pytest` + `requests`.
- Python 3.12.x is required (`pyproject.toml: requires-python = ">=3.12,<3.13"`).
- Secrets live in `config/config.json`; never commit credentials or tokens.
- Use type hints and descriptive docstrings like existing modules (see `utils/api/github_api.py`).
- Prefer small, single-responsibility helpers and keep HTTP logic inside `utils/http/client.py`.

## Patterns To Reuse
1. **API-wrapper-first** — Reach for `GitHubAPI` facade methods (`api.repos.*`, `api.users.*`, etc.) before hand-rolling HTTP `requests`. Reserve raw `http_client.get(...)` for explicit HTTP-shape validation.
2. **Constants over hardcoded strings** — Import endpoint paths, error codes, and HTTP status codes from `data/constants.py` instead of using hardcoded strings. This ensures consistency and makes refactoring easier.
3. **Four calling patterns** — Document which of the four patterns from README you are using and why. Inline comments are only necessary when deviating.
4. **REST context** — When constructing URLs manually, derive them from `data/constants.py` endpoint templates to stay environment agnostic.
5. **Stateful calls** — Wrap create/update/delete flows with `api.*` methods before assertions so local caches stay fresh.
6. **Database verification** — Use `utils/database/` helpers (e.g., `TestResultDB`) to record and verify test run data. See `.cursor/rules/35-database-utilities.mdc` for patterns.
7. **Rate limiting** — ALL API calls are automatically rate-limited via fixtures. Use `rate_limiter` for manual control. Never create unwrapped HTTP clients.

## Structure & Documentation
- Mirror the folder map from `README.md` when adding modules; helpers belong in `utils/`, tests under scoped subfolders (e.g., `tests/repos/`, `tests/users/`).
- **Universal utilities** (database, HTTP, testing) go directly under `utils/`. **Endpoint-specific helpers** go in subdirectories (e.g., `utils/repos/`, `utils/search/`).
- **All docstrings must follow Google style formatting** across the entire codebase (tests, utilities, fixtures).
- **Tests use rule-of-three docstrings**: Every test function includes a one-line summary, then sections for **Setup**, **Action**, and **Assertions**.

## Commands
- `make install` — Create venv and install dependencies
- `make test` — Run all tests
- `make test-repos` — Run repo tests only
- `make lint` — Run ruff + mypy + codespell
- `make format` — Auto-format with ruff
- `make check` — Run all pre-commit hooks
