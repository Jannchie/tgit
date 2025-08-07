# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TGIT is a Python CLI tool for Git workflow automation that provides AI-powered commit message generation, conventional commit formatting, changelog generation, and version management. It's built as a modern Python package using uv for dependency management.

## Development Commands

### Linting and Code Quality

```bash
# Run ruff linting (configured in pyproject.toml)
ruff check .

# Auto-fix ruff errors where possible
ruff check --fix .

# Run ruff formatting
ruff format .
```

### Build and Distribution

```bash
# Build the package
uv build

# Install package in development mode
uv pip install -e .

# Install dependencies (including dev dependencies)
uv sync

# Publish package (uses scripts/publish.sh)
./scripts/publish.sh
```

### Testing

```bash
# Run all tests with coverage
./scripts/test.sh

# Run only unit tests
./scripts/test.sh --unit

# Run only integration tests  
./scripts/test.sh --integration

# Run tests with verbose output
./scripts/test.sh --verbose

# Run tests with custom coverage threshold
./scripts/test.sh --coverage 85

# Run pytest directly (manual coverage control)
pytest tests/ --cov=tgit --cov-report=term-missing --cov-report=html:htmlcov
```

## Code Architecture

### Entry Point and CLI Structure

- `cli.py` - Main CLI entry point using Click with subcommands
- Each subcommand has its own module (commit.py, changelog.py, version.py, etc.)
- Rich library used for enhanced terminal output and progress bars
- Package entry point: `tgit = "tgit:cli.app"`

### Core Modules

- `commit.py` - Handles AI-powered commit message generation using OpenAI API
- `changelog.py` - Generates conventional commit-based changelogs with custom markdown rendering
- `version.py` - Semantic versioning with support for multiple project file types
- `add.py` - Simple git add wrapper
- `settings.py` - YAML-based configuration loading from global (~/.tgit.yaml) and workspace (.tgit.yaml) files
- `interactive_settings.py` - Interactive settings management CLI
- `shared.py` - Shared utilities including command execution and commit formatting
- `types.py` - Pydantic models and type definitions

### AI Integration

- OpenAI client configuration supports custom API URLs and keys
- Commit message generation uses structured output with Pydantic models
- Template-based prompts in `prompts/commit.txt` with Jinja2 templating
- Supports conventional commit types: feat, fix, chore, docs, style, refactor, perf, test, ci, version

### Configuration System

- Global settings: `~/.tgit.yaml` or `~/.tgit.yml`
- Workspace settings: `.tgit.yaml` or `.tgit.yml` in current directory
- Workspace settings override global settings
- Supports: apiKey, apiUrl, model, commit.emoji, commit.types, show_command, skip_confirm

### Version Management

- Supports multiple project file formats: package.json, pyproject.toml, setup.py, Cargo.toml, VERSION, VERSION.txt
- Semantic versioning with pre-release support
- Automatic version bumping based on conventional commits
- Integrates with git tagging and changelog generation

### Changelog Generation

- Custom Rich markdown renderer for enhanced terminal output
- Supports git remote URL detection for commit links
- Groups commits by type with breaking changes prioritized
- Generates markdown with author attribution and commit hashes
- Can prepend to existing CHANGELOG.md or create new files

## Important Implementation Details

### Git Operations

- Uses GitPython library for git operations
- Filters large files from AI diff analysis (>1000 lines)
- Handles renamed/moved files properly in diff generation
- Excludes .lock files from commit message generation but includes them in metadata

### Error Handling

- Graceful handling of missing OpenAI package
- Repository validation before operations
- File existence checks for version file updates
- Safe YAML loading with fallback to empty dict

### Dependencies

- Core: rich, pyyaml, questionary, gitpython, openai, jinja2, beautifulsoup4, click
- Build: hatchling via uv
- Code quality: ruff (configured for line length 140, extensive rule set)
- Testing: pytest, pytest-cov (via dev dependencies)
- Python version: 3.11+ required

## Testing Notes

- Test structure: `tests/unit/` for unit tests, `tests/integration/` for integration tests
- Coverage configured with pytest-cov; HTML reports generated in `htmlcov/`
- Use `./scripts/test.sh` for comprehensive testing with coverage
- 不要使用 ini_options 来自动 cov，而是需要手动传入参数进行覆盖率测试
