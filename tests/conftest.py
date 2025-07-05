import tempfile
from pathlib import Path
from unittest.mock import Mock

import git
import pytest

from tgit.version import Version


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Resolve symlinks to avoid path mismatch issues on macOS
        repo_path = Path(temp_dir).resolve()
        repo = git.Repo.init(repo_path)

        # Configure git user for testing
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        # Create initial commit
        test_file = repo_path / "test.txt"
        test_file.write_text("Initial content")
        repo.index.add([str(test_file)])
        repo.index.commit("Initial commit")

        yield repo_path, repo


@pytest.fixture
def sample_version():
    """Create a sample version for testing."""
    return Version(major=1, minor=2, patch=3)


@pytest.fixture
def sample_version_with_prerelease():
    """Create a sample version with prerelease for testing."""
    return Version(major=1, minor=2, patch=3, release="alpha")


@pytest.fixture
def sample_version_with_build():
    """Create a sample version with build metadata for testing."""
    return Version(major=1, minor=2, patch=3, build="build123")


@pytest.fixture
def mock_git_repo():
    """Mock git repository for unit tests."""
    mock_repo = Mock(spec=git.Repo)
    mock_repo.working_dir = "/fake/path"
    return mock_repo


@pytest.fixture
def sample_package_json(tmp_path):
    """Create a sample package.json file."""
    package_json = tmp_path / "package.json"
    package_json.write_text('{"name": "test-package", "version": "1.0.0"}')
    return tmp_path


@pytest.fixture
def sample_pyproject_toml(tmp_path):
    """Create a sample pyproject.toml file."""
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text("""
[project]
name = "test-package"
version = "1.0.0"
""")
    return tmp_path


@pytest.fixture
def sample_cargo_toml(tmp_path):
    """Create a sample Cargo.toml file."""
    cargo_toml = tmp_path / "Cargo.toml"
    cargo_toml.write_text("""
[package]
name = "test-package"
version = "1.0.0"
""")
    return tmp_path
