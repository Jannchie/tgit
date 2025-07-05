import json
from unittest.mock import patch

import pytest

from tgit.version import (
    Version,
    VersionArgs,
    get_current_version,
    get_prev_version,
    handle_version,
    update_version_files,
)


@pytest.mark.integration
class TestVersionIntegration:
    """Integration tests for version management workflow."""

    def test_get_prev_version_from_package_json(self, tmp_path):
        """Test getting previous version from package.json in real scenario."""
        # Create a real package.json file
        package_json = tmp_path / "package.json"
        package_json.write_text(json.dumps({"name": "test-package", "version": "1.2.3", "description": "A test package"}, indent=2))

        version = get_prev_version(str(tmp_path))

        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_get_prev_version_from_pyproject_toml(self, tmp_path):
        """Test getting previous version from pyproject.toml in real scenario."""
        # Create a real pyproject.toml file
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "test-package"
version = "2.1.0"
description = "A test package"
authors = [
    {name = "Test Author", email = "test@example.com"},
]
dependencies = []
""")

        version = get_prev_version(str(tmp_path))

        assert version is not None
        assert version.major == 2
        assert version.minor == 1
        assert version.patch == 0

    def test_get_prev_version_from_git_tags(self, temp_git_repo):
        """Test getting previous version from git tags."""
        repo_path, repo = temp_git_repo

        # Create a git tag
        repo.create_tag("v1.5.0")

        version = get_prev_version(str(repo_path))

        assert version is not None
        assert version.major == 1
        assert version.minor == 5
        assert version.patch == 0

    def test_get_prev_version_fallback_to_default(self, tmp_path):
        """Test fallback to default version when no version found."""
        # Create empty directory with no version files
        version = get_prev_version(str(tmp_path))

        assert version is not None
        assert version.major == 0
        assert version.minor == 0
        assert version.patch == 0

    def test_get_current_version_with_console_output(self, tmp_path, capsys):
        """Test get_current_version with console output."""
        # Create version file
        version_file = tmp_path / "VERSION"
        version_file.write_text("1.0.0")

        version = get_current_version(str(tmp_path), verbose=1)

        assert version is not None
        assert version.major == 1
        assert version.minor == 0
        assert version.patch == 0

        # Check console output
        captured = capsys.readouterr()
        assert "Bumping version..." in captured.out
        assert "Getting current version..." in captured.out
        assert "Previous version:" in captured.out

    def test_update_version_files_package_json(self, tmp_path):
        """Test updating version in package.json file."""
        # Create initial package.json
        package_json = tmp_path / "package.json"
        initial_content = {"name": "test-package", "version": "1.0.0", "description": "Test package"}
        package_json.write_text(json.dumps(initial_content, indent=2))

        # Create version args
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=True,
            no_tag=True,
            no_push=True,
            patch=False,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=str(tmp_path),
        )

        next_version = Version(major=1, minor=1, patch=0)

        # Update version files
        update_version_files(args, next_version, verbose=0, reclusive=False)

        # Verify update
        updated_content = json.loads(package_json.read_text())
        assert updated_content["version"] == "1.1.0"
        assert updated_content["name"] == "test-package"  # Other fields preserved

    def test_update_version_files_pyproject_toml(self, tmp_path):
        """Test updating version in pyproject.toml file."""
        # Create initial pyproject.toml
        pyproject_toml = tmp_path / "pyproject.toml"
        initial_content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "test-package"
version = "1.0.0"
description = "Test package"
"""
        pyproject_toml.write_text(initial_content)

        # Create version args
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=True,
            no_tag=True,
            no_push=True,
            patch=False,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=str(tmp_path),
        )

        next_version = Version(major=2, minor=0, patch=0)

        # Update version files
        update_version_files(args, next_version, verbose=0, reclusive=False)

        # Verify update
        updated_content = pyproject_toml.read_text()
        assert 'version = "2.0.0"' in updated_content
        assert 'name = "test-package"' in updated_content  # Other fields preserved

    def test_update_version_files_multiple_files(self, tmp_path):
        """Test updating version in multiple files."""
        # Create multiple version files
        package_json = tmp_path / "package.json"
        package_json.write_text('{"name": "test", "version": "1.0.0"}')

        version_file = tmp_path / "VERSION"
        version_file.write_text("1.0.0")

        # Create version args
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=True,
            no_tag=True,
            no_push=True,
            patch=False,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=str(tmp_path),
        )

        next_version = Version(major=1, minor=0, patch=1)

        # Update version files
        update_version_files(args, next_version, verbose=0, reclusive=False)

        # Verify updates
        updated_package_json = json.loads(package_json.read_text())
        assert updated_package_json["version"] == "1.0.1"

        updated_version_file = version_file.read_text().strip()
        assert updated_version_file == "1.0.1"

    def test_update_version_files_recursive(self, tmp_path):
        """Test updating version files recursively."""
        # Create nested directory structure
        subdir = tmp_path / "subproject"
        subdir.mkdir()

        # Create version files in different directories
        root_package_json = tmp_path / "package.json"
        root_package_json.write_text('{"name": "root", "version": "1.0.0"}')

        sub_package_json = subdir / "package.json"
        sub_package_json.write_text('{"name": "sub", "version": "1.0.0"}')

        # Create version args with recursive flag
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=True,
            no_tag=True,
            no_push=True,
            patch=False,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=True,
            custom="",
            path=str(tmp_path),
        )

        next_version = Version(major=1, minor=1, patch=0)

        # Update version files
        update_version_files(args, next_version, verbose=0, reclusive=True)

        # Verify updates in both directories
        root_content = json.loads(root_package_json.read_text())
        assert root_content["version"] == "1.1.0"

        sub_content = json.loads(sub_package_json.read_text())
        assert sub_content["version"] == "1.1.0"

    def test_update_version_files_ignore_node_modules(self, tmp_path):
        """Test that recursive update ignores node_modules directory."""
        # Create node_modules directory
        node_modules = tmp_path / "node_modules" / "some-package"
        node_modules.mkdir(parents=True)

        # Create package.json in node_modules (should be ignored)
        node_modules_package_json = node_modules / "package.json"
        node_modules_package_json.write_text('{"name": "dep", "version": "1.0.0"}')

        # Create package.json in root (should be updated)
        root_package_json = tmp_path / "package.json"
        root_package_json.write_text('{"name": "root", "version": "1.0.0"}')

        # Create version args with recursive flag
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=True,
            no_tag=True,
            no_push=True,
            patch=False,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=True,
            custom="",
            path=str(tmp_path),
        )

        next_version = Version(major=2, minor=0, patch=0)

        # Update version files
        update_version_files(args, next_version, verbose=0, reclusive=True)

        # Verify root package.json was updated
        root_content = json.loads(root_package_json.read_text())
        assert root_content["version"] == "2.0.0"

        # Verify node_modules package.json was NOT updated
        node_modules_content = json.loads(node_modules_package_json.read_text())
        assert node_modules_content["version"] == "1.0.0"

    @patch("tgit.version.get_next_version")
    @patch("tgit.version.get_current_version")
    @patch("tgit.version.update_version_files")
    @patch("tgit.version.execute_git_commands")
    @patch("tgit.version.questionary.confirm")
    def test_handle_version_without_changelog(self, mock_prompt, mock_execute_git, mock_update_files, mock_get_current, mock_get_next):
        """Test handle_version without changelog generation."""
        # Setup mocks
        mock_get_current.return_value = Version(major=1, minor=0, patch=0)
        mock_get_next.return_value = Version(major=1, minor=1, patch=0)
        mock_prompt.return_value.ask.return_value = False

        # Create args
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=False,
            no_tag=False,
            no_push=False,
            patch=False,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=".",
        )

        # Mock changelog handling
        with patch("tgit.changelog.handle_changelog") as mock_handle_changelog:
            handle_version(args)

            # Verify changelog was NOT generated
            mock_handle_changelog.assert_not_called()

    @patch("tgit.version.get_next_version")
    @patch("tgit.version.get_current_version")
    def test_handle_version_cancelled(self, mock_get_current, mock_get_next):
        """Test handle_version when user cancels version selection."""
        # Setup mocks
        mock_get_current.return_value = Version(major=1, minor=0, patch=0)
        mock_get_next.return_value = None  # User cancelled

        # Create args
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=False,
            no_tag=False,
            no_push=False,
            patch=False,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=".",
        )

        # Should not raise any errors and should return early
        handle_version(args)

        # Verify get_next_version was called
        mock_get_next.assert_called_once()


@pytest.mark.integration
@pytest.mark.slow
class TestVersionGitIntegration:
    """Integration tests with real git operations."""

    def test_version_workflow_with_git_repo(self, temp_git_repo):
        """Test complete version workflow with real git repository."""
        repo_path, repo = temp_git_repo

        # Create package.json
        package_json = repo_path / "package.json"
        package_json.write_text('{"name": "test", "version": "1.0.0"}')

        # Add and commit package.json
        repo.index.add([str(package_json)])
        repo.index.commit("Add package.json")

        # Get current version
        current_version = get_current_version(str(repo_path), verbose=0)
        assert current_version.major == 1
        assert current_version.minor == 0
        assert current_version.patch == 0

        # Create version args for patch bump
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=True,
            no_tag=True,
            no_push=True,
            patch=True,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=str(repo_path),
        )

        # Update version files
        next_version = Version(major=1, minor=0, patch=1)
        update_version_files(args, next_version, verbose=0, reclusive=False)

        # Verify version was updated
        updated_content = json.loads(package_json.read_text())
        assert updated_content["version"] == "1.0.1"

        # Verify git status shows changes
        assert repo.is_dirty()

        # Verify the specific file was modified
        changed_files = [item.a_path for item in repo.index.diff(None)]
        assert "package.json" in changed_files

    def test_version_detection_priority_with_git_tags(self, temp_git_repo):
        """Test that file versions take priority over git tags."""
        repo_path, repo = temp_git_repo

        # Create git tag
        repo.create_tag("v2.0.0")

        # Create package.json with different version
        package_json = repo_path / "package.json"
        package_json.write_text('{"name": "test", "version": "1.5.0"}')

        # Should prefer package.json over git tag
        version = get_prev_version(str(repo_path))
        assert version.major == 1
        assert version.minor == 5
        assert version.patch == 0

    def test_version_from_git_when_no_files(self, temp_git_repo):
        """Test version detection from git when no version files exist."""
        repo_path, repo = temp_git_repo

        # Create git tag
        repo.create_tag("v3.1.4")

        # Should use git tag when no version files exist
        version = get_prev_version(str(repo_path))
        assert version.major == 3
        assert version.minor == 1
        assert version.patch == 4
