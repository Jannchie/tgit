# 🚀 TGIT - Tool for Git Interaction Temptation

[![CodeTime Badge](https://shields.jannchie.com/endpoint?style=social&color=222&url=https%3A%2F%2Fapi.codetime.dev%2Fv3%2Fusers%2Fshield%3Fuid%3D2%26project%3Dtgit)](https://codetime.dev)
[![codecov](https://codecov.io/gh/Jannchie/tgit/graph/badge.svg?token=YQE0LPE7JX)](https://codecov.io/gh/Jannchie/tgit)
[![PyPI version](https://badge.fury.io/py/tgit.svg)](https://badge.fury.io/py/tgit)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An elegant CLI tool that simplifies and streamlines your Git workflow with AI-powered commit messages, automated changelog generation, and intelligent version management.

## ✨ Features

### 🤖 AI-Powered Commits

- Generate conventional commit messages automatically using OpenAI
- Smart diff analysis that focuses on meaningful changes
- Support for custom commit types and emojis
- Breaking change detection

### 📝 Automated Changelog

- Generate beautiful, structured changelogs from conventional commits
- Group commits by type with emoji categorization
- Support for multiple output formats
- Automatic git remote URL detection for commit links

### 🔢 Intelligent Version Management

- Semantic versioning with pre-release support
- Support for multiple project files (package.json, pyproject.toml, Cargo.toml, etc.)
- Automatic version bumping based on commit history
- Git tagging integration

### ⚙️ Flexible Configuration

- Global and workspace-specific settings
- YAML-based configuration files
- Interactive settings management
- Customizable commit types and emojis

## 🚀 Quick Start

### Installation

```bash
pip install tgit
```

### Basic Usage

```bash
# AI-powered commit with automatic message generation
tgit commit

# Generate changelog for current version
tgit changelog

# Bump version and generate changelog
tgit version

# Interactive settings configuration
tgit settings
```

### Configuration

The easiest way to configure TGIT is through the interactive settings command:

```bash
# Interactive configuration - recommended!
tgit settings
```

This will guide you through setting up:

- OpenAI API key for AI-powered commits
- Preferred AI model (gpt-4, gpt-3.5-turbo, etc.)
- Commit emoji preferences
- Custom commit types

Alternatively, you can manually create a `.tgit.yaml` file in your project root or `~/.tgit.yaml` for global settings:

```yaml
apiKey: "your-openai-api-key"
model: "gpt-4"
commit:
  emoji: true
  types:
    - type: "feat"
      emoji: "✨"
    - type: "fix"
      emoji: "🐛"
```

## 📖 Commands

### Commit

```bash
# AI-powered commit
tgit commit 

# Breaking change commit
tgit commit --breaking "remove deprecated api"
```

### Changelog

```bash
# Generate changelog for current version
tgit changelog

# Generate changelog from specific version
tgit changelog --from v1.0.0

# Generate changelog to specific version
tgit changelog --to v2.0.0
```

### Version

```bash
# Interactive version bump
tgit version

# Bump specific version type
tgit version --patch
tgit version --minor
tgit version --major

# Pre-release version
tgit version --prerelease alpha
```

### Settings

```bash
# Interactive settings configuration
tgit settings

# Show current settings
tgit settings --show
```

## 🛠️ Development

### Setup

```bash
# Clone the repository
git clone https://github.com/Jannchie/tgit.git
cd tgit

# Install with uv
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
./scripts/test.sh

# Run with coverage
./scripts/test.sh --coverage 90

# Run specific test types
./scripts/test.sh --unit
./scripts/test.sh --integration
```

### Code Quality

```bash
# Run linting
ruff check .

# Run formatting
ruff format .

# Build package
uv build
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📞 Support

If you encounter any problems or have suggestions, please [open an issue](https://github.com/Jannchie/tgit/issues) on GitHub.
