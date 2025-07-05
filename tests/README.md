# TGIT Testing Suite

This directory contains comprehensive tests for the TGIT project using pytest.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_version.py      # Tests for version.py module
│   └── test_changelog.py    # Tests for changelog.py module
├── integration/             # Integration tests (slower, with real dependencies)
│   └── test_version_integration.py
└── README.md               # This file
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
uv add --group test pytest pytest-cov pytest-mock pytest-xdist
```

### Quick Start

Run all tests with coverage:
```bash
pytest
```

### Test Scripts

Use the provided test script for more options:
```bash
# Run all tests
./scripts/test.sh

# Run only unit tests
./scripts/test.sh --unit

# Run only integration tests
./scripts/test.sh --integration

# Run with verbose output
./scripts/test.sh --verbose

# Run with custom coverage threshold
./scripts/test.sh --coverage 90

# Watch mode (re-run tests on file changes)
./scripts/test.sh --watch
```

### Manual Commands

```bash
# Run specific test file
pytest tests/unit/test_version.py

# Run specific test class
pytest tests/unit/test_version.py::TestVersion

# Run specific test method
pytest tests/unit/test_version.py::TestVersion::test_version_creation

# Run with coverage
pytest --cov=tgit --cov-report=html

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v

# Run slow tests only
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests that test individual functions and classes without external dependencies.

- **TestVersion**: Tests for Version class creation, string conversion, and parsing
- **TestVersionChoice**: Tests for version bump choices and calculations
- **TestVersionParsing**: Tests for extracting versions from various file formats
- **TestVersionBumping**: Tests for version bumping logic
- **TestVersionArgsHandling**: Tests for command-line argument handling
- **TestNewVersionFunctions**: Tests for the refactored version functions

### Integration Tests (`tests/integration/`)

Slower tests that test the interaction between components and with real dependencies like git repositories.

- **TestVersionIntegration**: Tests complete version workflows
- **TestVersionGitIntegration**: Tests with real git repositories

## Coverage Reports

Coverage reports are generated in multiple formats:

- **Terminal**: Shows missing lines in the terminal output
- **HTML**: Detailed report in `htmlcov/index.html`
- **XML**: Machine-readable report in `coverage.xml`

### Viewing Coverage

Open the HTML coverage report:
```bash
# On macOS
open htmlcov/index.html

# On Linux
xdg-open htmlcov/index.html

# Or serve it locally
python -m http.server 8000 -d htmlcov
```

## VSCode Integration

The project includes VSCode configuration for seamless testing:

### Features

- **Test Discovery**: Automatic test discovery and display in the Test Explorer
- **Coverage Gutters**: Visual coverage indicators in the editor
- **Debug Support**: Debug tests directly from VSCode
- **Test Running**: Run tests with keyboard shortcuts

### Setup

1. Install recommended extensions (prompted automatically)
2. Tests will appear in the Test Explorer panel
3. Use Ctrl/Cmd+Shift+P and search for "Python: Configure Tests" if needed

### Launch Configurations

Available debug configurations:
- **Python: Run Tests** - Run all tests with debugging
- **Python: Run Unit Tests** - Run only unit tests
- **Python: Run Integration Tests** - Run only integration tests
- **TGIT: Version Command** - Debug the version command

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `temp_git_repo`: Creates a temporary git repository for testing
- `sample_version`: Sample Version instance
- `sample_version_with_prerelease`: Version with prerelease
- `sample_version_with_build`: Version with build metadata
- `mock_git_repo`: Mocked git repository
- `sample_package_json`: Temporary package.json file
- `sample_pyproject_toml`: Temporary pyproject.toml file
- `sample_cargo_toml`: Temporary Cargo.toml file

## Writing Tests

### Unit Test Example

```python
def test_version_creation():
    """Test Version object creation."""
    version = Version(major=1, minor=2, patch=3)
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
```

### Integration Test Example

```python
@pytest.mark.integration
def test_version_workflow_with_git_repo(self, temp_git_repo):
    """Test complete version workflow with real git repository."""
    repo_path, repo = temp_git_repo
    # Test implementation...
```

### Using Fixtures

```python
def test_with_temp_file(tmp_path):
    """Test using temporary directory fixture."""
    test_file = tmp_path / "test.json"
    test_file.write_text('{"version": "1.0.0"}')
    # Test implementation...
```

## Markers

Tests can be marked with categories:

- `@pytest.mark.unit`: Unit tests (default for tests/unit/)
- `@pytest.mark.integration`: Integration tests (default for tests/integration/)
- `@pytest.mark.slow`: Slow tests that can be skipped

## CI/CD Integration

The test suite is designed to work well with CI/CD systems:

- **Exit codes**: Proper exit codes for pass/fail
- **JUnit XML**: Can generate JUnit XML for CI systems
- **Coverage data**: Exports coverage data in multiple formats
- **Parallel execution**: Supports parallel test execution

### Example CI Commands

```bash
# For GitHub Actions, GitLab CI, etc.
pytest --junitxml=test-results.xml --cov=tgit --cov-report=xml
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're running tests from the project root
2. **Git errors in tests**: Ensure git is configured with user.name and user.email
3. **Permission errors**: Check file permissions on test scripts
4. **Coverage too low**: Adjust coverage threshold in pyproject.toml

### Debug Tips

```bash
# Run with more verbose output
pytest -vvs

# Drop into debugger on failure
pytest --pdb

# Show local variables in tracebacks
pytest --tb=long

# Capture output even for passing tests
pytest -s
```