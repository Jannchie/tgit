# Repository Guidelines

## Project Structure & Module Organization

- `tgit/` holds the Python package and CLI entry point. Key modules include `cli.py`, `commit.py`, `changelog.py`, `version.py`, and `settings.py`.
- `tgit/prompts/` contains Jinja2 prompt templates used by the AI commit flow.
- `tgit/utils/` hosts shared helpers.
- `tests/` is split into `tests/unit/` and `tests/integration/`, with shared fixtures in `tests/conftest.py`.
- `scripts/` contains automation such as `scripts/test.sh` and `scripts/publish.sh`.
- Generated artifacts live in `dist/`, `htmlcov/`, and `coverage.xml`.

## Build, Test, and Development Commands

- `uv sync` installs dependencies (use this for a fresh dev environment).
- `uv pip install -e ".[dev]"` installs in editable mode with dev tools.
- `uv run ruff check .` runs linting (strict rules configured in `pyproject.toml`).
- `uv run ruff format .` applies formatting (line length 140).
- `./scripts/test.sh` runs the full test suite with coverage and a configurable threshold.
- `uv run pytest tests/unit/` runs unit tests directly when you want faster feedback.
- `uv build` builds the package for distribution.

## Coding Style & Naming Conventions

- Python 3.11+ only, 4-space indentation.
- Keep type hints for function parameters and return values.
- Follow ruff defaults plus repository rules; avoid unused imports and keep lines under 140 characters.
- Names: `snake_case` for modules/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.

## Testing Guidelines

- Framework: `pytest` with `pytest-cov`.
- Naming patterns (from `pyproject.toml`): files `test_*.py` or `*_test.py`, classes `Test*`, functions `test_*`.
- Markers: `unit`, `integration`, `slow` (use `-m "not slow"` to skip).
- Coverage reports are generated in `htmlcov/` and `coverage.xml` via `scripts/test.sh`.

## Commit & Pull Request Guidelines

- Commit messages follow an emoji prefix plus Conventional Commit style. Example: `:sparkles: feat(version): add --no-recursive option to version command`.
- Release commits use `:bookmark: version: vX.Y.Z`.
- PRs should describe the change, list tests run, and link related issues. Include screenshots only for CLI output or documentation changes.

## Configuration & Secrets

- Local settings live in `.tgit.yaml` (workspace) or `~/.tgit.yaml` (global). Do not commit real API keys or tokens.
