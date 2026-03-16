.PHONY: help install sync format lint check test test-% lock clean

PYTHON ?= python3
PYTEST_ARGS ?= -v

# Detect if uv is available
UV := $(shell command -v uv 2> /dev/null)

help:
	@echo "Available targets:"
	@echo "  install    – Create .venv, install dependencies, and install pre-commit hooks"
	@echo "  sync       – Install from uv.lock (reproducible, requires uv)"
	@echo "  format     – Format code with ruff"
	@echo "  lint       – Run ruff format check, ruff linter, mypy type checking, and codespell"
	@echo "  check      – Run all pre-commit hooks"
	@echo "  test       – Run all tests"
	@echo "  test-<mark> – Run tests with marker (e.g., test-repos, test-users, test-orgs)"
	@echo "  lock       – Regenerate uv.lock and requirements.txt from pyproject.toml"
	@echo "  clean      – Remove cache and generated files"

install:
ifdef UV
	uv venv .venv
	VIRTUAL_ENV="$(PWD)/.venv" uv pip install -r requirements.txt
else
	$(PYTHON) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
endif
	.venv/bin/pre-commit install

sync:
ifdef UV
	UV_PROJECT_ENVIRONMENT=.venv uv sync --frozen
	UV_PROJECT_ENVIRONMENT=.venv uv run pre-commit install
	@echo "Environment synced from uv.lock"
else
	@echo "Error: uv is required for 'make sync'. Install it with:"
	@echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
	@exit 1
endif

format:
	ruff format .

lint:
	ruff format --check .
	ruff check --fix .
	mypy .
	pre-commit run codespell --all-files

check:
	pre-commit run --all-files

test:
	pytest $(PYTEST_ARGS)

test-%:
	pytest -m $* $(PYTEST_ARGS)

lock:
ifdef UV
	uv lock
	uv export --no-hashes -o requirements.txt
else
	@echo "Error: uv is required for 'make lock'."
	@exit 1
endif

clean:
	rm -rf .pytest_cache .mypy_cache allure-results .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
