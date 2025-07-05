# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TGIT is a Python CLI tool for Git workflow automation that provides AI-powered commit message generation, conventional commit formatting, changelog generation, and version management. It's built as a modern Python package using uv for dependency management.

## Development Commands

### Linting and Code Quality

```bash
# Run ruff linting (configured in pyproject.toml)
ruff check .

# Run ruff formatting
ruff format .
```

### Build and Distribution

```bash
# Build the package
uv build

# Install package in development mode
uv pip install -e .

# Publish package (uses scripts/publish.sh)
./scripts/publish.sh
```

### Testing

No specific test framework is configured. Check if tests exist before adding new functionality.

## Code Architecture

### Entry Point and CLI Structure

- `cli.py` - Main CLI entry point using argparse with subcommands
- Each subcommand has its own module (commit.py, changelog.py, version.py, etc.)
- Rich library used for enhanced terminal output and progress bars

### Core Modules

- `commit.py` - Handles AI-powered commit message generation using OpenAI API
- `changelog.py` - Generates conventional commit-based changelogs with custom markdown rendering
- `version.py` - Semantic versioning with support for multiple project file types
- `add.py` - Simple git add wrapper
- `config.py` - Configuration management for API keys and settings
- `settings.py` - YAML-based configuration loading from global (~/.tgit.yaml) and workspace (.tgit.yaml) files
- `utils.py` - Shared utilities including command execution and commit formatting

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

- Core: rich, pyyaml, inquirer, gitpython, openai, jinja2, beautifulsoup4
- Build: hatchling via uv
- Code quality: ruff (configured for line length 140, extensive rule set)
