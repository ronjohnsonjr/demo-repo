# Code Quality & Linting

## Tools
- **ruff** — Linting and formatting (replaces flake8, isort, black)
- **mypy** — Type checking with `check_untyped_defs = true`
- **codespell** — Spell checking in code and comments
- **pre-commit** — Runs all checks before every commit

## Configuration
All tool config lives in `pyproject.toml`. Key settings:
- Line length: 120
- Target: Python 3.12
- Enabled rule sets: E, W, F, I, N, UP, B, S, A, C4, DTZ, T20, SIM, LOG

## Running Checks
```bash
make lint    # ruff format --check + ruff check + mypy + codespell
make format  # ruff format (auto-fix)
make check   # all pre-commit hooks
```
