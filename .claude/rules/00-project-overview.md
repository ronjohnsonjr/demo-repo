# Project Overview

GitHub REST API pytest automation framework. Environment expectations and global
coding conventions that every change should respect.

## Key Facts
- This repo drives GitHub REST API tests with `pytest` + `requests`.
- Python 3.12.x is required (`pyproject.toml: requires-python = ">=3.12,<3.13"`).
- Secrets live in `config/config.json`; never commit credentials or tokens.
- Use type hints and descriptive docstrings like existing modules (see `utils/api/github_api.py`).
- Prefer small, single-responsibility helpers and keep HTTP logic inside `utils/http/client.py`.

## Patterns To Reuse
1. **API-wrapper-first** — Use `GitHubAPI` facade methods before hand-rolling HTTP requests.
2. **Constants over hardcoded strings** — Import from `data/constants.py`.
3. **Rate limiting** — All API calls go through the rate-limited HTTP client.
4. **Database verification** — Use `utils/database/` helpers for test-result tracking.
