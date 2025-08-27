from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from click.testing import CliRunner

from tgit.version import (
    Version,
    VersionArgs,
    VersionChoice,
    _apply_version_choice,
    _get_default_bump_from_commits,
    _handle_explicit_version_args,
    _handle_interactive_version_selection,
    _has_explicit_version_args,
    _parse_gitignore,
    _prompt_for_version_choice,
    _should_ignore_path,
    bump_version,
    execute_git_commands,
    format_diff_lines,
    get_current_version,
    get_custom_version,
    get_default_bump_by_commits_dict,
    get_detected_files,
    get_next_version,
    get_pre_release_identifier,
    get_root_detected_files,
    get_version_from_cargo_toml,
    get_version_from_files,
    get_version_from_git,
    get_version_from_package_json,
    get_version_from_pyproject_toml,
    get_version_from_setup_py,
    get_version_from_version_file,
    get_version_from_version_txt,
    handle_version,
    show_file_diff,
    update_cargo_toml_version,
    update_file,
    update_version_files,
    update_version_in_file,
    version,
)


class TestVersion:
    """Test cases for Version class."""

    def test_version_creation(self):
        """Test Version object creation."""
        version = Version(major=1, minor=2, patch=3)
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.release is None
        assert version.build is None

    def test_version_creation_with_prerelease(self):
        """Test Version object creation with prerelease."""
        version = Version(major=1, minor=2, patch=3, release="alpha")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.release == "alpha"
        assert version.build is None

    def test_version_creation_with_build(self):
        """Test Version object creation with build metadata."""
        version = Version(major=1, minor=2, patch=3, build="build123")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.release is None
        assert version.build == "build123"

    def test_version_str_basic(self):
        """Test string representation of basic version."""
        version = Version(major=1, minor=2, patch=3)
        assert str(version) == "1.2.3"

    def test_version_str_with_prerelease(self):
        """Test string representation with prerelease."""
        version = Version(major=1, minor=2, patch=3, release="alpha")
        assert str(version) == "1.2.3-alpha"

    def test_version_str_with_build(self):
        """Test string representation with build metadata."""
        version = Version(major=1, minor=2, patch=3, build="build123")
        assert str(version) == "1.2.3+build123"

    def test_version_str_with_prerelease_and_build(self):
        """Test string representation with both prerelease and build."""
        version = Version(major=1, minor=2, patch=3, release="alpha", build="build123")
        assert str(version) == "1.2.3-alpha+build123"

    def test_version_from_str_basic(self):
        """Test creating Version from string."""
        version = Version.from_str("1.2.3")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.release is None
        assert version.build is None

    def test_version_from_str_with_prerelease(self):
        """Test creating Version from string with prerelease."""
        version = Version.from_str("1.2.3-alpha")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.release == "alpha"
        assert version.build is None

    def test_version_from_str_with_build(self):
        """Test creating Version from string with build."""
        version = Version.from_str("1.2.3+build123")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.release is None
        assert version.build == "build123"

    def test_version_from_str_with_prerelease_and_build(self):
        """Test creating Version from string with prerelease and build."""
        version = Version.from_str("1.2.3-alpha+build123")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.release == "alpha"
        assert version.build == "build123"

    def test_version_from_str_invalid(self):
        """Test creating Version from invalid string."""
        with pytest.raises(ValueError, match="Invalid version format"):
            Version.from_str("invalid")

    def test_version_from_str_empty(self):
        """Test creating Version from empty string."""
        with pytest.raises(ValueError, match="Invalid version format"):
            Version.from_str("")


class TestVersionChoice:
    """Test cases for VersionChoice class."""

    def test_version_choice_patch(self):
        """Test VersionChoice for patch bump."""
        prev_version = Version(major=1, minor=2, patch=3)
        choice = VersionChoice(prev_version, "patch")
        assert choice.bump == "patch"
        assert choice.next_version.major == 1
        assert choice.next_version.minor == 2
        assert choice.next_version.patch == 4

    def test_version_choice_minor(self):
        """Test VersionChoice for minor bump."""
        prev_version = Version(major=1, minor=2, patch=3)
        choice = VersionChoice(prev_version, "minor")
        assert choice.bump == "minor"
        assert choice.next_version.major == 1
        assert choice.next_version.minor == 3
        assert choice.next_version.patch == 0

    def test_version_choice_major(self):
        """Test VersionChoice for major bump."""
        prev_version = Version(major=1, minor=2, patch=3)
        choice = VersionChoice(prev_version, "major")
        assert choice.bump == "major"
        assert choice.next_version.major == 2
        assert choice.next_version.minor == 0
        assert choice.next_version.patch == 0

    def test_version_choice_prepatch(self):
        """Test VersionChoice for prepatch bump."""
        prev_version = Version(major=1, minor=2, patch=3)
        choice = VersionChoice(prev_version, "prepatch")
        assert choice.bump == "prepatch"
        assert choice.next_version.major == 1
        assert choice.next_version.minor == 2
        assert choice.next_version.patch == 4
        assert choice.next_version.release == "{RELEASE}"

    def test_version_choice_major_removes_prerelease(self):
        """Test VersionChoice removes prerelease suffix for major bump to create stable release."""
        prev_version = Version(major=0, minor=5, patch=0, release="beta")
        choice = VersionChoice(prev_version, "major")
        assert choice.bump == "major"
        assert choice.next_version.major == 1
        assert choice.next_version.minor == 0
        assert choice.next_version.patch == 0
        assert choice.next_version.release is None
        assert choice.next_version.build is None

    def test_version_choice_minor_removes_prerelease(self):
        """Test VersionChoice removes prerelease suffix for minor bump to create stable release."""
        prev_version = Version(major=0, minor=5, patch=0, release="beta")
        choice = VersionChoice(prev_version, "minor")
        assert choice.bump == "minor"
        assert choice.next_version.major == 0
        assert choice.next_version.minor == 6
        assert choice.next_version.patch == 0
        assert choice.next_version.release is None
        assert choice.next_version.build is None

    def test_version_choice_patch_removes_prerelease(self):
        """Test VersionChoice removes prerelease suffix for patch bump to create stable release."""
        prev_version = Version(major=0, minor=5, patch=0, release="beta")
        choice = VersionChoice(prev_version, "patch")
        assert choice.bump == "patch"
        assert choice.next_version.major == 0
        assert choice.next_version.minor == 5
        assert choice.next_version.patch == 1
        assert choice.next_version.release is None
        assert choice.next_version.build is None

    def test_version_choice_release_removes_prerelease_suffix(self):
        """Test VersionChoice with 'release' removes prerelease suffix without changing version numbers."""
        prev_version = Version(major=1, minor=0, patch=0, release="beta")
        choice = VersionChoice(prev_version, "release")
        assert choice.bump == "release"
        assert choice.next_version.major == 1
        assert choice.next_version.minor == 0
        assert choice.next_version.patch == 0
        assert choice.next_version.release is None
        assert choice.next_version.build is None

    def test_version_choice_release_with_build_metadata(self):
        """Test VersionChoice with 'release' removes both prerelease and build metadata."""
        prev_version = Version(major=2, minor=1, patch=3, release="rc.1", build="20231201")
        choice = VersionChoice(prev_version, "release")
        assert choice.bump == "release"
        assert choice.next_version.major == 2
        assert choice.next_version.minor == 1
        assert choice.next_version.patch == 3
        assert choice.next_version.release is None
        assert choice.next_version.build is None

    @patch("tgit.version._prompt_for_version_choice")
    @patch("tgit.version._apply_version_choice")
    def test_handle_interactive_version_selection_includes_release_for_prerelease(self, mock_apply, mock_prompt):
        """Test that 'release' option is included when current version is prerelease."""
        prev_version = Version(1, 0, 0, release="beta")
        mock_choice = Mock()
        mock_choice.bump = "release"
        mock_prompt.return_value = mock_choice
        mock_apply.return_value = Version(1, 0, 0)
        
        _handle_interactive_version_selection(prev_version, "patch", 0)
        
        # Verify that _prompt_for_version_choice was called with choices including 'release'
        assert mock_prompt.called
        choices_arg = mock_prompt.call_args[0][0]
        bump_types = [choice.bump for choice in choices_arg]
        assert "release" in bump_types
        assert bump_types[0] == "release"  # Should be first option for prominence

    @patch("tgit.version._prompt_for_version_choice")
    @patch("tgit.version._apply_version_choice")
    def test_handle_interactive_version_selection_no_release_for_stable(self, mock_apply, mock_prompt):
        """Test that 'release' option is not included when current version is stable."""
        prev_version = Version(1, 0, 0)  # No prerelease suffix
        mock_choice = Mock()
        mock_choice.bump = "patch"
        mock_prompt.return_value = mock_choice
        mock_apply.return_value = Version(1, 0, 1)
        
        _handle_interactive_version_selection(prev_version, "patch", 0)
        
        # Verify that _prompt_for_version_choice was called with choices not including 'release'
        assert mock_prompt.called
        choices_arg = mock_prompt.call_args[0][0]
        bump_types = [choice.bump for choice in choices_arg]
        assert "release" not in bump_types

    def test_version_choice_str(self):
        """Test string representation of VersionChoice."""
        prev_version = Version(major=1, minor=2, patch=3)
        choice = VersionChoice(prev_version, "patch")
        assert str(choice) == "patch (1.2.4)"


class TestVersionParsing:
    """Test cases for version parsing from files."""

    def test_get_version_from_package_json(self, tmp_path):
        """Test extracting version from package.json."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"name": "test", "version": "1.2.3"}')

        version = get_version_from_package_json(tmp_path)
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_get_version_from_package_json_missing(self, tmp_path):
        """Test extracting version from missing package.json."""
        version = get_version_from_package_json(tmp_path)
        assert version is None

    def test_get_version_from_package_json_no_version(self, tmp_path):
        """Test extracting version from package.json without version field."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"name": "test"}')

        version = get_version_from_package_json(tmp_path)
        assert version is None

    def test_get_version_from_package_json_invalid_version(self, tmp_path):
        """Test extracting invalid version from package.json returns None."""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"version": "invalid-version"}')

        version = get_version_from_package_json(tmp_path)
        assert version is None

    def test_get_version_from_pyproject_toml(self, tmp_path):
        """Test extracting version from pyproject.toml."""
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[project]
name = "test"
version = "1.2.3"
""")

        version = get_version_from_pyproject_toml(tmp_path)
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_get_version_from_pyproject_toml_poetry(self, tmp_path):
        """Test extracting version from pyproject.toml with poetry."""
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[tool.poetry]
name = "test"
version = "1.2.3"
""")

        version = get_version_from_pyproject_toml(tmp_path)
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_get_version_from_setup_py(self, tmp_path):
        """Test extracting version from setup.py."""
        setup_py = tmp_path / "setup.py"
        setup_py.write_text("""
from setuptools import setup

setup(
    name="test",
    version="1.2.3",
)
""")

        version = get_version_from_setup_py(tmp_path)
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_get_version_from_cargo_toml(self, tmp_path):
        """Test extracting version from Cargo.toml."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text("""
[package]
name = "test"
version = "1.2.3"
""")

        version = get_version_from_cargo_toml(tmp_path)
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_get_version_from_version_file(self, tmp_path):
        """Test extracting version from VERSION file."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3")

        version = get_version_from_version_file(tmp_path)
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_get_version_from_version_txt(self, tmp_path):
        """Test extracting version from VERSION.txt file."""
        version_txt = tmp_path / "VERSION.txt"
        version_txt.write_text("1.2.3")

        version = get_version_from_version_txt(tmp_path)
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_get_version_from_files_priority(self, tmp_path):
        """Test version extraction priority from multiple files."""
        # Create multiple version files
        package_json = tmp_path / "package.json"
        package_json.write_text('{"version": "1.0.0"}')

        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[project]
version = "2.0.0"
""")

        # Should prefer package.json (first in priority)
        version = get_version_from_files(tmp_path)
        assert version is not None
        assert version.major == 1
        assert version.minor == 0
        assert version.patch == 0


class TestVersionBumping:
    """Test cases for version bumping logic."""

    def test_bump_version_patch(self):
        """Test patch version bump."""
        prev_version = Version(major=1, minor=2, patch=3)
        target = VersionChoice(prev_version, "patch")
        next_version = Version(major=1, minor=2, patch=3)

        bump_version(target, next_version)

        assert next_version.major == 1
        assert next_version.minor == 2
        assert next_version.patch == 4

    def test_bump_version_minor(self):
        """Test minor version bump."""
        prev_version = Version(major=1, minor=2, patch=3)
        target = VersionChoice(prev_version, "minor")
        next_version = Version(major=1, minor=2, patch=3)

        bump_version(target, next_version)

        assert next_version.major == 1
        assert next_version.minor == 3
        assert next_version.patch == 0

    def test_bump_version_major(self):
        """Test major version bump."""
        prev_version = Version(major=1, minor=2, patch=3)
        target = VersionChoice(prev_version, "major")
        next_version = Version(major=1, minor=2, patch=3)

        bump_version(target, next_version)

        assert next_version.major == 2
        assert next_version.minor == 0
        assert next_version.patch == 0

    def test_get_default_bump_by_commits_dict_breaking_v0(self):
        """Test default bump for breaking changes in v0.x.x."""
        prev_version = Version(major=0, minor=1, patch=0)
        commits_by_type = {"breaking": [Mock()]}

        bump = get_default_bump_by_commits_dict(commits_by_type, prev_version)  # type: ignore

        assert bump == "minor"

    def test_get_default_bump_by_commits_dict_breaking_v1(self):
        """Test default bump for breaking changes in v1+."""
        prev_version = Version(major=1, minor=0, patch=0)
        commits_by_type = {"breaking": [Mock()]}

        bump = get_default_bump_by_commits_dict(commits_by_type, prev_version)  # type: ignore

        assert bump == "major"

    def test_get_default_bump_by_commits_dict_feat(self):
        """Test default bump for feat commits."""
        prev_version = Version(major=1, minor=0, patch=0)
        commits_by_type = {"feat": [Mock()]}

        bump = get_default_bump_by_commits_dict(commits_by_type, prev_version)  # type: ignore

        assert bump == "minor"

    def test_get_default_bump_by_commits_dict_patch(self):
        """Test default bump for patch commits."""
        prev_version = Version(major=1, minor=0, patch=0)
        commits_by_type = {"fix": [Mock()]}

        bump = get_default_bump_by_commits_dict(commits_by_type, prev_version)  # type: ignore

        assert bump == "patch"


class TestVersionArgsHandling:
    """Test cases for version args handling."""

    def test_has_explicit_version_args_patch(self):
        """Test explicit version args detection for patch."""
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=False,
            no_tag=False,
            no_push=False,
            patch=True,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=".",
        )

        assert _has_explicit_version_args(args) is True

    def test_has_explicit_version_args_none(self):
        """Test explicit version args detection when none specified."""
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

        assert _has_explicit_version_args(args) is False

    def test_handle_explicit_version_args_patch(self):
        """Test handling explicit patch version args."""
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=False,
            no_tag=False,
            no_push=False,
            patch=True,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=".",
        )
        prev_version = Version(major=1, minor=2, patch=3)

        result = _handle_explicit_version_args(args, prev_version)

        assert result is not None
        assert result.major == 1
        assert result.minor == 2
        assert result.patch == 4

    def test_handle_explicit_version_args_minor(self):
        """Test handling explicit minor version args."""
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=False,
            no_tag=False,
            no_push=False,
            patch=False,
            minor=True,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=".",
        )
        prev_version = Version(major=1, minor=2, patch=3)

        result = _handle_explicit_version_args(args, prev_version)

        assert result is not None
        assert result.major == 1
        assert result.minor == 3
        assert result.patch == 0

    def test_handle_explicit_version_args_major(self):
        """Test handling explicit major version args."""
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=False,
            no_tag=False,
            no_push=False,
            patch=False,
            minor=False,
            major=True,
            prepatch="",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=".",
        )
        prev_version = Version(major=1, minor=2, patch=3)

        result = _handle_explicit_version_args(args, prev_version)

        assert result is not None
        assert result.major == 2
        assert result.minor == 0
        assert result.patch == 0

    def test_handle_explicit_version_args_prepatch(self):
        """Test handling explicit prepatch version args."""
        args = VersionArgs(
            version="",
            verbose=0,
            no_commit=False,
            no_tag=False,
            no_push=False,
            patch=False,
            minor=False,
            major=False,
            prepatch="alpha",
            preminor="",
            premajor="",
            recursive=False,
            custom="",
            path=".",
        )
        prev_version = Version(major=1, minor=2, patch=3)

        result = _handle_explicit_version_args(args, prev_version)

        assert result is not None
        assert result.major == 1
        assert result.minor == 2
        assert result.patch == 4
        assert result.release == "alpha"


class TestNewVersionFunctions:
    """Test cases for the new refactored version functions."""

    @patch("tgit.version.get_commits")
    @patch("tgit.version.get_git_commits_range")
    @patch("tgit.version.group_commits_by_type")
    @patch("tgit.version.get_default_bump_by_commits_dict")
    @patch("tgit.version.git.Repo")
    def test_get_default_bump_from_commits(
        self, mock_repo, mock_get_default_bump, mock_group_commits, mock_get_commits_range, mock_get_commits
    ):
        """Test _get_default_bump_from_commits function."""
        # Setup mocks
        mock_repo.return_value = Mock()
        mock_get_commits_range.return_value = ("HEAD~10", "HEAD")
        mock_get_commits.return_value = []
        mock_group_commits.return_value = {"feat": [Mock()]}
        mock_get_default_bump.return_value = "minor"

        prev_version = Version(major=1, minor=0, patch=0)
        result = _get_default_bump_from_commits("/fake/path", prev_version, 0)

        assert result == "minor"
        mock_repo.assert_called_once_with("/fake/path")
        mock_get_default_bump.assert_called_once()

    @patch("tgit.version.console")
    @patch("tgit.version._prompt_for_version_choice")
    @patch("tgit.version._apply_version_choice")
    def test_handle_interactive_version_selection(self, mock_apply, mock_prompt, mock_console):
        """Test _handle_interactive_version_selection function."""
        # Setup mocks
        mock_choice = Mock()
        mock_choice.bump = "patch"
        mock_prompt.return_value = mock_choice
        mock_result = Version(major=1, minor=2, patch=4)
        mock_apply.return_value = mock_result

        prev_version = Version(major=1, minor=2, patch=3)
        result = _handle_interactive_version_selection(prev_version, "patch", 0)

        assert result == mock_result
        mock_prompt.assert_called_once()
        mock_apply.assert_called_once_with(mock_choice, prev_version)

    @patch("tgit.version.questionary.select")
    def test_prompt_for_version_choice_success(self, mock_prompt):
        """Test _prompt_for_version_choice success case."""
        prev_version = Version(major=1, minor=2, patch=3)
        choice = VersionChoice(prev_version, "patch")
        mock_prompt.return_value.ask.return_value = choice

        result = _prompt_for_version_choice([choice], choice)

        assert result == choice
        mock_prompt.assert_called_once()

    @patch("tgit.version.questionary.select")
    def test_prompt_for_version_choice_cancelled(self, mock_prompt):
        """Test _prompt_for_version_choice when user cancels."""
        prev_version = Version(major=1, minor=2, patch=3)
        choice = VersionChoice(prev_version, "patch")
        mock_prompt.return_value.ask.return_value = None

        result = _prompt_for_version_choice([choice], choice)

        assert result is None

    @patch("tgit.version.questionary.select")
    def test_prompt_for_version_choice_invalid_type(self, mock_prompt):
        """Test _prompt_for_version_choice with invalid type."""
        prev_version = Version(major=1, minor=2, patch=3)
        choice = VersionChoice(prev_version, "patch")
        mock_prompt.return_value.ask.return_value = "invalid"

        with pytest.raises(TypeError, match="Expected VersionChoice"):
            _prompt_for_version_choice([choice], choice)

    @patch("tgit.version.get_pre_release_identifier")
    @patch("tgit.version.bump_version")
    def test_apply_version_choice_prepatch(self, mock_bump, mock_get_pre_release):
        """Test _apply_version_choice for prepatch."""
        prev_version = Version(major=1, minor=2, patch=3)
        target = VersionChoice(prev_version, "prepatch")
        mock_get_pre_release.return_value = "alpha"

        result = _apply_version_choice(target, prev_version)

        assert result is not None
        assert result.release == "alpha"
        mock_bump.assert_called_once_with(target, result)
        mock_get_pre_release.assert_called_once()

    @patch("tgit.version.get_pre_release_identifier")
    @patch("tgit.version.bump_version")
    def test_apply_version_choice_prepatch_cancelled(self, mock_bump, mock_get_pre_release):
        """Test _apply_version_choice for prepatch when user cancels."""
        prev_version = Version(major=1, minor=2, patch=3)
        target = VersionChoice(prev_version, "prepatch")
        mock_get_pre_release.return_value = None

        result = _apply_version_choice(target, prev_version)

        assert result is None

    @patch("tgit.version.get_custom_version")
    @patch("tgit.version.bump_version")
    def test_apply_version_choice_custom(self, mock_bump, mock_get_custom):
        """Test _apply_version_choice for custom version."""
        prev_version = Version(major=1, minor=2, patch=3)
        target = VersionChoice(prev_version, "custom")
        custom_version = Version(major=2, minor=0, patch=0)
        mock_get_custom.return_value = custom_version

        result = _apply_version_choice(target, prev_version)

        assert result == custom_version
        mock_bump.assert_not_called()  # bump_version should NOT be called for custom versions
        mock_get_custom.assert_called_once()

    @patch("tgit.version._get_default_bump_from_commits")
    @patch("tgit.version._handle_explicit_version_args")
    @patch("tgit.version._has_explicit_version_args")
    def test_get_next_version_explicit_args(self, mock_has_explicit, mock_handle_explicit, mock_get_default_bump):
        """Test get_next_version with explicit args."""
        args = Mock()
        args.path = "/fake/path"
        prev_version = Version(major=1, minor=2, patch=3)

        mock_has_explicit.return_value = True
        expected_version = Version(major=1, minor=2, patch=4)
        mock_handle_explicit.return_value = expected_version

        result = get_next_version(args, prev_version, 0)

        assert result == expected_version
        mock_has_explicit.assert_called_once_with(args)
        mock_handle_explicit.assert_called_once_with(args, prev_version)
        mock_get_default_bump.assert_not_called()

    @patch("tgit.version._get_default_bump_from_commits")
    @patch("tgit.version._handle_interactive_version_selection")
    @patch("tgit.version._has_explicit_version_args")
    def test_get_next_version_interactive(self, mock_has_explicit, mock_handle_interactive, mock_get_default_bump):
        """Test get_next_version with interactive selection."""
        args = Mock()
        args.path = "/fake/path"
        prev_version = Version(major=1, minor=2, patch=3)

        mock_has_explicit.return_value = False
        mock_get_default_bump.return_value = "patch"
        expected_version = Version(major=1, minor=2, patch=4)
        mock_handle_interactive.return_value = expected_version

        result = get_next_version(args, prev_version, 0)

        assert result == expected_version
        mock_has_explicit.assert_called_once_with(args)
        mock_get_default_bump.assert_called_once_with("/fake/path", prev_version, 0)
        mock_handle_interactive.assert_called_once_with(prev_version, "patch", 0)

    def test_get_next_version_none_prev_version(self):
        """Test get_next_version with None previous version."""
        args = Mock()
        args.path = "/fake/path"

        with (
            patch("tgit.version._get_default_bump_from_commits"),
            patch("tgit.version._has_explicit_version_args") as mock_has_explicit,
            patch("tgit.version._handle_explicit_version_args") as mock_handle_explicit,
        ):
            mock_has_explicit.return_value = True
            mock_handle_explicit.return_value = Version(major=0, minor=0, patch=1)

            result = get_next_version(args, None, 0)

            assert result is not None
            # Should create default Version(0, 0, 0) when prev_version is None
            mock_handle_explicit.assert_called_once()
            call_args = mock_handle_explicit.call_args[0]
            assert call_args[1].major == 0
            assert call_args[1].minor == 0
            assert call_args[1].patch == 0


class TestShowFileDiff:
    @patch("tgit.version.questionary.confirm")
    def test_show_file_diff_user_confirms(self, mock_confirm):
        """Test show_file_diff when user confirms."""
        mock_confirm.return_value.ask.return_value = True
        old_content = "line1\nline2"
        new_content = "line1\nline3"
        show_file_diff(old_content, new_content, "test.txt")
        mock_confirm.assert_called_once_with("Do you want to continue?", default=True)

    @patch("tgit.version.questionary.confirm")
    def test_show_file_diff_user_cancels(self, mock_confirm):
        """Test show_file_diff when user cancels."""
        mock_confirm.return_value.ask.return_value = False
        old_content = "line1\nline2"
        new_content = "line1\nline3"
        with pytest.raises(SystemExit):
            show_file_diff(old_content, new_content, "test.txt")
        mock_confirm.assert_called_once_with("Do you want to continue?", default=True)


class TestCargoTomlVersionUpdate:
    """Test cases for Cargo.toml version updating."""

    def test_update_cargo_toml_version_package_section_only(self, tmp_path):
        """Test that update_cargo_toml_version only updates version in [package] section."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml_content = """[package]
name = "test-package"
version = "1.0.0"
authors = ["Test Author"]

[dependencies]
serde = { version = "1.0.0", features = ["derive"] }

[dev-dependencies]
tokio = { version = "1.0.0", features = ["full"] }

[workspace]
members = ["subcrate"]

# Some other version reference that should NOT be changed
# version = "should-not-change"
"""
        cargo_toml.write_text(cargo_toml_content)

        # Update version
        update_cargo_toml_version(str(cargo_toml), "2.0.0", 0, show_diff=False)

        # Read updated content
        updated_content = cargo_toml.read_text()

        # Verify only the package version was updated
        assert 'version = "2.0.0"' in updated_content
        assert 'serde = { version = "1.0.0"' in updated_content  # Dependency version unchanged
        assert 'tokio = { version = "1.0.0"' in updated_content  # Dev dependency version unchanged
        assert '# version = "should-not-change"' in updated_content  # Comment unchanged

        # Count occurrences to ensure only one version was changed
        assert updated_content.count('version = "2.0.0"') == 1
        assert updated_content.count('version = "1.0.0"') == 2  # The two dependency versions remain

    def test_update_cargo_toml_version_complex_package_section(self, tmp_path):
        """Test updating version in a more complex [package] section."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml_content = """[package]
name = "complex-package"
version = "0.1.0"
edition = "2021"
authors = ["Author One", "Author Two"]
license = "MIT"
description = "A test package"
repository = "https://github.com/test/test"

[lib]
name = "complex_package"
path = "src/lib.rs"

[dependencies]
log = { version = "0.4.0" }

[workspace]
members = ["other-crate"]
"""
        cargo_toml.write_text(cargo_toml_content)

        update_cargo_toml_version(str(cargo_toml), "0.2.0", 0, show_diff=False)

        updated_content = cargo_toml.read_text()

        # Verify correct update
        assert 'version = "0.2.0"' in updated_content
        assert 'log = { version = "0.4.0" }' in updated_content  # Dependency unchanged
        assert updated_content.count('version = "0.2.0"') == 1
        assert updated_content.count('version = "0.4.0"') == 1

    def test_update_cargo_toml_version_file_not_exists(self, tmp_path):
        """Test that function handles non-existent file gracefully."""
        non_existent_file = str(tmp_path / "nonexistent.toml")

        # Should not raise an error
        update_cargo_toml_version(non_existent_file, "1.0.0", 0, show_diff=False)


class TestParseGitignore:
    """Test cases for _parse_gitignore function."""

    def test_parse_gitignore_existing_file(self, tmp_path):
        """Test parsing an existing gitignore file."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\nnode_modules/\n# This is a comment\nvenv\n\n")

        patterns = _parse_gitignore(gitignore)

        expected = ["*.log", "node_modules/", "venv"]
        assert patterns == expected

    def test_parse_gitignore_missing_file(self, tmp_path):
        """Test parsing a non-existent gitignore file."""
        gitignore = tmp_path / ".gitignore"

        patterns = _parse_gitignore(gitignore)

        assert patterns == []

    def test_parse_gitignore_empty_file(self, tmp_path):
        """Test parsing an empty gitignore file."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("")

        patterns = _parse_gitignore(gitignore)

        assert patterns == []

    def test_parse_gitignore_only_comments(self, tmp_path):
        """Test parsing gitignore file with only comments."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("# Comment 1\n# Comment 2\n")

        patterns = _parse_gitignore(gitignore)

        assert patterns == []

    def test_parse_gitignore_mixed_content(self, tmp_path):
        """Test parsing gitignore file with mixed content."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("""# Node
node_modules/
*.log

# Python
__pycache__/
*.pyc

# Virtual environments
venv/
.venv/
""")

        patterns = _parse_gitignore(gitignore)

        expected = ["node_modules/", "*.log", "__pycache__/", "*.pyc", "venv/", ".venv/"]
        assert patterns == expected

    def test_parse_gitignore_unicode_error(self, tmp_path):
        """Test parsing gitignore file with unicode decode error."""
        gitignore = tmp_path / ".gitignore"

        # Write binary data that would cause UnicodeDecodeError
        with gitignore.open("wb") as f:
            f.write(b"\xff\xfe*.log\n")

        patterns = _parse_gitignore(gitignore)

        # Should handle the error gracefully and return empty list
        assert patterns == []


class TestShouldIgnorePath:
    """Test cases for _should_ignore_path function."""

    def test_should_ignore_virtual_env_dirs(self, tmp_path):
        """Test ignoring common virtual environment directories."""
        root_path = tmp_path

        # Test various virtual env directory names
        venv_dirs = ["venv", ".venv", "env", ".env", "virtualenv", ".virtualenv"]

        for venv_dir in venv_dirs:
            test_path = root_path / venv_dir / "package.json"
            result = _should_ignore_path(test_path, root_path, [])
            assert result is True, f"Should ignore {venv_dir}"

    def test_should_ignore_build_dirs(self, tmp_path):
        """Test ignoring common build directories."""
        root_path = tmp_path

        build_dirs = ["__pycache__", "node_modules", "dist", "build", ".git"]

        for build_dir in build_dirs:
            test_path = root_path / build_dir / "some_file.txt"
            result = _should_ignore_path(test_path, root_path, [])
            assert result is True, f"Should ignore {build_dir}"

    def test_should_ignore_site_packages(self, tmp_path):
        """Test ignoring site-packages directory."""
        root_path = tmp_path
        test_path = root_path / "lib" / "python3.9" / "site-packages" / "package.json"

        result = _should_ignore_path(test_path, root_path, [])

        assert result is True

    def test_should_not_ignore_regular_dirs(self, tmp_path):
        """Test not ignoring regular directories."""
        root_path = tmp_path
        test_path = root_path / "src" / "components" / "package.json"

        result = _should_ignore_path(test_path, root_path, [])

        assert result is False

    def test_should_ignore_gitignore_patterns(self, tmp_path):
        """Test ignoring paths based on gitignore patterns."""
        root_path = tmp_path
        gitignore_patterns = ["*.log", "temp/", "build/*"]

        # Test file pattern
        log_file = root_path / "debug.log"
        result = _should_ignore_path(log_file, root_path, gitignore_patterns)
        assert result is True

        # Test directory pattern
        temp_file = root_path / "temp" / "file.txt"
        result = _should_ignore_path(temp_file, root_path, gitignore_patterns)
        assert result is True

        # Test glob pattern
        build_file = root_path / "build" / "output.js"
        result = _should_ignore_path(build_file, root_path, gitignore_patterns)
        assert result is True

    def test_should_not_ignore_non_matching_patterns(self, tmp_path):
        """Test not ignoring paths that don't match gitignore patterns."""
        root_path = tmp_path
        gitignore_patterns = ["*.log", "temp/"]

        # Test non-matching file
        js_file = root_path / "index.js"
        result = _should_ignore_path(js_file, root_path, gitignore_patterns)
        assert result is False

        # Test non-matching directory
        src_file = root_path / "src" / "file.txt"
        result = _should_ignore_path(src_file, root_path, gitignore_patterns)
        assert result is False

    def test_should_ignore_nested_paths(self, tmp_path):
        """Test ignoring nested paths correctly."""
        root_path = tmp_path
        gitignore_patterns = ["*/node_modules/*"]

        # Test deeply nested node_modules
        nested_file = root_path / "project" / "node_modules" / "package" / "index.js"
        result = _should_ignore_path(nested_file, root_path, gitignore_patterns)
        assert result is True


class TestGetDetectedFilesWithIgnore:
    """Test cases for the modified get_detected_files function with ignore functionality."""

    def test_get_detected_files_ignores_venv(self, tmp_path):
        """Test that get_detected_files ignores virtual environment directories."""
        # Create test structure
        (tmp_path / "package.json").write_text('{"version": "1.0.0"}')
        (tmp_path / "venv").mkdir()
        (tmp_path / "venv" / "package.json").write_text('{"version": "2.0.0"}')
        (tmp_path / ".venv").mkdir()
        (tmp_path / ".venv" / "package.json").write_text('{"version": "3.0.0"}')
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "package.json").write_text('{"version": "4.0.0"}')

        files = get_detected_files(str(tmp_path))

        # Should find root and src package.json, but not venv ones
        assert len(files) == 2
        file_paths = [str(f.relative_to(tmp_path)) for f in files]
        assert "package.json" in file_paths
        assert "src/package.json" in file_paths
        assert "venv/package.json" not in file_paths
        assert ".venv/package.json" not in file_paths

    def test_get_detected_files_respects_gitignore(self, tmp_path):
        """Test that get_detected_files respects .gitignore patterns."""
        # Create test structure
        (tmp_path / "package.json").write_text('{"version": "1.0.0"}')
        (tmp_path / "temp").mkdir()
        (tmp_path / "temp" / "package.json").write_text('{"version": "2.0.0"}')
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "package.json").write_text('{"version": "3.0.0"}')

        # Create .gitignore
        (tmp_path / ".gitignore").write_text("temp/\n*.log\n")

        files = get_detected_files(str(tmp_path))

        # Should find root and src package.json, but not temp ones
        assert len(files) == 2
        file_paths = [str(f.relative_to(tmp_path)) for f in files]
        assert "package.json" in file_paths
        assert "src/package.json" in file_paths
        assert "temp/package.json" not in file_paths

    def test_get_detected_files_no_gitignore(self, tmp_path):
        """Test get_detected_files when no .gitignore exists."""
        # Create test structure
        (tmp_path / "package.json").write_text('{"version": "1.0.0"}')
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "package.json").write_text('{"version": "2.0.0"}')

        files = get_detected_files(str(tmp_path))

        # Should find both files
        assert len(files) == 2
        file_paths = [str(f.relative_to(tmp_path)) for f in files]
        assert "package.json" in file_paths
        assert "src/package.json" in file_paths

    def test_get_detected_files_complex_structure(self, tmp_path):
        """Test get_detected_files with a complex directory structure."""
        # Create complex test structure
        (tmp_path / "package.json").write_text('{"version": "1.0.0"}')
        (tmp_path / "pyproject.toml").write_text('[project]\nversion = "2.0.0"')

        # Create directories to ignore
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "package.json").write_text('{"version": "ignored"}')
        (tmp_path / "venv").mkdir()
        (tmp_path / "venv" / "pyproject.toml").write_text('[project]\nversion = "ignored"')

        # Create regular directories
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "package.json").write_text('{"version": "3.0.0"}')
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "VERSION").write_text("4.0.0")

        # Create .gitignore
        (tmp_path / ".gitignore").write_text("*.log\nbuild/\n")

        files = get_detected_files(str(tmp_path))

        # Should find root package.json, pyproject.toml, src package.json, and tests VERSION
        assert len(files) == 4
        file_paths = [str(f.relative_to(tmp_path)) for f in files]

        # Expected files
        expected_files = ["package.json", "pyproject.toml", "src/package.json", "tests/VERSION"]
        for expected in expected_files:
            assert expected in file_paths

        # Should not include ignored files
        assert "node_modules/package.json" not in file_paths
        assert "venv/pyproject.toml" not in file_paths


class TestVersionChoiceStr:
    """Test VersionChoice __str__ method."""

    def test_version_choice_str_with_next_version(self):
        """Test VersionChoice.__str__ when next_version is automatically set."""
        prev_version = Version(1, 2, 3)
        choice = VersionChoice(bump="patch", previous_version=prev_version)

        result = str(choice)

        assert result == "patch (1.2.4)"  # patch increments the patch version

    def test_version_choice_str_without_next_version(self):
        """Test VersionChoice.__str__ when next_version is manually removed."""
        prev_version = Version(1, 2, 3)
        choice = VersionChoice(bump="patch", previous_version=prev_version)

        # Manually delete next_version to test the fallback
        del choice.next_version
        result = str(choice)

        assert result == "patch"


class TestGetVersionFromFilesErrorHandling:
    """Test error handling in version file parsing functions."""

    def test_get_version_from_setup_py(self, tmp_path):
        """Test get_version_from_setup_py function."""
        setup_py = tmp_path / "setup.py"
        setup_py.write_text("from setuptools import setup\nsetup(version='1.2.3')")

        result = get_version_from_setup_py(tmp_path)

        assert result == Version(1, 2, 3)

    def test_get_version_from_cargo_toml_decode_error(self, tmp_path):
        """Test get_version_from_cargo_toml with TOML decode error."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text('[package\nversion = "1.0.0"')  # Invalid TOML

        with patch("tgit.version.console.print") as mock_print:
            result = get_version_from_cargo_toml(tmp_path)

            assert result is None
            mock_print.assert_called()

    def test_get_version_from_cargo_toml_read_error(self, tmp_path):
        """Test get_version_from_cargo_toml with file read error."""
        with (
            patch("pathlib.Path.read_text", side_effect=OSError("Permission denied")),
            patch("tgit.version.console.print") as mock_print,
        ):
            result = get_version_from_cargo_toml(tmp_path)

            assert result is None
            mock_print.assert_called()

    def test_get_version_from_cargo_toml_missing_package_table(self, tmp_path):
        """Test get_version_from_cargo_toml with missing package table."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text('[dependencies]\nserde = "1.0"')  # No package table

        with patch("tgit.version.console.print") as mock_print:
            result = get_version_from_cargo_toml(tmp_path)

            assert result is None
            mock_print.assert_called()

    def test_get_version_from_cargo_toml_invalid_package_table(self, tmp_path):
        """Test get_version_from_cargo_toml with invalid package table."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text('package = "not a table"')  # Invalid package

        with patch("tgit.version.console.print") as mock_print:
            result = get_version_from_cargo_toml(tmp_path)

            assert result is None
            mock_print.assert_called()

    def test_get_version_from_cargo_toml_missing_version(self, tmp_path):
        """Test get_version_from_cargo_toml with missing version in package table."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text('[package]\nname = "test"')  # No version

        with patch("tgit.version.console.print") as mock_print:
            result = get_version_from_cargo_toml(tmp_path)

            assert result is None
            mock_print.assert_called()

    def test_get_version_from_cargo_toml_empty_version(self, tmp_path):
        """Test get_version_from_cargo_toml with empty version string."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text('[package]\nversion = ""')  # Empty version

        with patch("tgit.version.console.print") as mock_print:
            result = get_version_from_cargo_toml(tmp_path)

            assert result is None
            mock_print.assert_called()

    def test_get_version_from_version_file(self, tmp_path):
        """Test get_version_from_version_file function."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("2.1.0")

        result = get_version_from_version_file(tmp_path)

        assert result == Version(2, 1, 0)

    def test_get_version_from_version_txt(self, tmp_path):
        """Test get_version_from_version_txt function."""
        version_file = tmp_path / "VERSION.txt"
        version_file.write_text("3.0.1")

        result = get_version_from_version_txt(tmp_path)

        assert result == Version(3, 0, 1)


class TestGetCurrentVersion:
    """Test get_current_version function."""

    @patch("tgit.version.get_prev_version")
    @patch("tgit.version.console")
    def test_get_current_version_verbose(self, mock_console, mock_get_prev):
        """Test get_current_version with verbose output."""
        mock_version = Version(1, 2, 3)
        mock_get_prev.return_value = mock_version

        result = get_current_version(".", verbose=1)

        assert result == mock_version
        mock_console.print.assert_called()
        mock_console.status.assert_called()

    @patch("tgit.version.get_prev_version")
    @patch("tgit.version.console")
    def test_get_current_version_not_verbose(self, mock_console, mock_get_prev):
        """Test get_current_version without verbose output."""
        mock_version = Version(2, 0, 0)
        mock_get_prev.return_value = mock_version

        result = get_current_version(".", verbose=0)

        assert result == mock_version
        mock_console.status.assert_called()


class TestUpdateCargoTomlVersionErrorHandling:
    """Test update_cargo_toml_version error handling."""

    def test_update_cargo_toml_version_file_not_exists(self, tmp_path):
        """Test update_cargo_toml_version when file doesn't exist."""
        non_existent_file = tmp_path / "nonexistent" / "Cargo.toml"

        # This should just return without doing anything when file doesn't exist
        update_cargo_toml_version(str(non_existent_file), "1.0.0", verbose=0)

        # Should not raise any exception

    def test_update_cargo_toml_version_complex_package_section(self, tmp_path):
        """Test update_cargo_toml_version with complex package section."""
        cargo_toml = tmp_path / "Cargo.toml"
        content = """[package]
name = "my_package"
version = "0.1.0"
authors = ["Author <author@example.com>"]
description = "A package"

[dependencies]
serde = "1.0"
"""
        cargo_toml.write_text(content)

        # Mock the confirmation to avoid interactive prompt
        with patch("tgit.version.questionary.confirm") as mock_confirm:
            mock_confirm.return_value.ask.return_value = True
            update_cargo_toml_version(str(cargo_toml), "1.2.3", verbose=0, show_diff=False)

        updated_content = cargo_toml.read_text()
        assert 'version = "1.2.3"' in updated_content
        assert 'name = "my_package"' in updated_content
        assert 'serde = "1.0"' in updated_content


class TestPreReleaseVersionHandling:
    """Test pre-release version handling functionality."""

    def test_apply_version_choice_prepatch(self):
        """Test _apply_version_choice with prepatch."""
        prev_version = Version(1, 2, 3)
        target = VersionChoice(bump="prepatch", previous_version=prev_version)

        with patch("tgit.version.questionary.text") as mock_text:
            mock_text.return_value.ask.return_value = "alpha"
            result = _apply_version_choice(target, prev_version)

            assert result == Version(1, 2, 4, release="alpha")

    def test_apply_version_choice_custom(self):
        """Test _apply_version_choice with custom version."""
        prev_version = Version(1, 2, 3)
        target = VersionChoice(bump="custom", previous_version=prev_version)

        with patch("tgit.version.questionary.text") as mock_text:
            mock_text.return_value.ask.return_value = "5.0.0"
            result = _apply_version_choice(target, prev_version)

            assert result == Version(5, 0, 0)


class TestVersionFromFilesErrorHandling:
    """Test error handling in version file parsing."""

    def test_get_version_from_files_flit_support(self, tmp_path):
        """Test get_version_from_files with flit-style pyproject.toml."""
        pyproject_toml = tmp_path / "pyproject.toml"
        content = """
[build-system]
requires = ["flit_core >=3.2,<4"]
build-backend = "flit_core.buildapi"

[project]
version = "1.2.3"
"""
        pyproject_toml.write_text(content)

        result = get_version_from_files(tmp_path)

        assert result == Version(1, 2, 3)

    def test_get_version_from_files_setuptools_support(self, tmp_path):
        """Test get_version_from_files with project.version style."""
        pyproject_toml = tmp_path / "pyproject.toml"
        content = """
[project]
version = "2.1.0"
"""
        pyproject_toml.write_text(content)

        result = get_version_from_files(tmp_path)

        assert result == Version(2, 1, 0)

    def test_get_version_from_files_priority_order(self, tmp_path):
        """Test get_version_from_files respects priority order."""
        # Create multiple version files with different priorities
        (tmp_path / "package.json").write_text('{"version": "1.0.0"}')
        (tmp_path / "pyproject.toml").write_text('[project]\nversion = "2.0.0"')
        (tmp_path / "setup.py").write_text('from setuptools import setup\nsetup(version="3.0.0")')
        (tmp_path / "Cargo.toml").write_text('[package]\nversion = "4.0.0"')
        (tmp_path / "VERSION").write_text("5.0.0")
        (tmp_path / "VERSION.txt").write_text("6.0.0")

        result = get_version_from_files(tmp_path)

        # Should return the highest priority version (package.json = priority 1)
        assert result == Version(1, 0, 0)

    def test_get_version_from_pyproject_toml_no_version_key(self, tmp_path):
        """Test get_version_from_pyproject_toml with missing version key."""
        pyproject_toml = tmp_path / "pyproject.toml"
        content = """
[project]
name = "test-package"
"""
        pyproject_toml.write_text(content)

        result = get_version_from_pyproject_toml(tmp_path)

        assert result is None

    def test_get_version_from_package_json_no_version_key(self, tmp_path):
        """Test get_version_from_package_json with missing version key."""
        package_json = tmp_path / "package.json"
        content = '{"name": "test-package"}'
        package_json.write_text(content)

        result = get_version_from_package_json(tmp_path)

        assert result is None


class TestBumpVersionErrorHandling:
    """Test bump_version function error handling."""

    @patch("tgit.version.get_detected_files")
    @patch("tgit.version.get_root_detected_files")
    @patch("tgit.version.get_current_version")
    @patch("tgit.version.console")
    def test_bump_version_no_version_files(self, mock_console, mock_get_current, mock_get_root_files, mock_get_files):
        """Test handle_version when no version files found."""
        mock_get_files.return_value = []
        mock_get_root_files.return_value = []
        mock_get_current.return_value = Version.from_str("1.0.0")

        # Create mock args
        args = Mock()
        args.path = "/fake/path"
        args.recursive = False
        args.verbose = 0  # Set verbose as integer, not Mock

        # This should handle the case gracefully and print message about no files
        handle_version(args)

        # Should print the message about no version files detected
        mock_console.print.assert_any_call("No version files detected for update.")


class TestExecuteGitCommands:
    """Test cases for execute_git_commands function."""

    @patch("tgit.version.run_command")
    @patch("tgit.version.get_commit_command")
    @patch("tgit.version.settings")
    def test_execute_git_commands_all_operations(self, mock_settings, mock_get_commit_command, mock_run_command):
        """Test execute_git_commands with all operations enabled."""
        # Setup
        args = VersionArgs(
            version="1.0.0",
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
        next_version = Version(1, 0, 0)
        mock_settings.commit.emoji = True
        mock_get_commit_command.return_value = "git commit -m ':bookmark: version: v1.0.0'"

        # Execute
        execute_git_commands(args, next_version, 0)

        # Verify
        expected_commands = ["git add .", "git commit -m ':bookmark: version: v1.0.0'", "git tag v1.0.0", "git push", "git push --tag"]
        expected_commands_str = "\n".join(expected_commands)
        mock_run_command.assert_called_once_with(mock_settings, expected_commands_str)
        mock_get_commit_command.assert_called_once_with("version", None, "v1.0.0", use_emoji=True)

    @patch("tgit.version.run_command")
    @patch("tgit.version.console")
    @patch("tgit.version.settings")
    def test_execute_git_commands_no_commit(self, mock_settings, mock_console, mock_run_command):
        """Test execute_git_commands with no_commit=True."""
        # Setup
        args = VersionArgs(
            version="1.0.0",
            verbose=1,
            no_commit=True,
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
        next_version = Version(1, 0, 0)

        # Execute
        execute_git_commands(args, next_version, 1)

        # Verify
        mock_console.print.assert_any_call("Skipping commit")
        expected_commands = ["git tag v1.0.0", "git push", "git push --tag"]
        expected_commands_str = "\n".join(expected_commands)
        mock_run_command.assert_called_once_with(mock_settings, expected_commands_str)

    @patch("tgit.version.run_command")
    @patch("tgit.version.console")
    @patch("tgit.version.settings")
    def test_execute_git_commands_no_tag(self, mock_settings, mock_console, mock_run_command):
        """Test execute_git_commands with no_tag=True."""
        # Setup
        args = VersionArgs(
            version="1.0.0",
            verbose=1,
            no_commit=False,
            no_tag=True,
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
        next_version = Version(1, 0, 0)
        mock_settings.commit.emoji = False

        # Execute
        execute_git_commands(args, next_version, 1)

        # Verify
        mock_console.print.assert_any_call("Skipping tag")

    @patch("tgit.version.run_command")
    @patch("tgit.version.console")
    @patch("tgit.version.settings")
    def test_execute_git_commands_no_push(self, mock_settings, mock_console, mock_run_command):
        """Test execute_git_commands with no_push=True."""
        # Setup
        args = VersionArgs(
            version="1.0.0",
            verbose=1,
            no_commit=False,
            no_tag=False,
            no_push=True,
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
        next_version = Version(1, 0, 0)

        # Execute
        execute_git_commands(args, next_version, 1)

        # Verify
        mock_console.print.assert_any_call("Skipping push")

    @patch("tgit.version.run_command")
    @patch("tgit.version.settings")
    def test_execute_git_commands_all_disabled(self, mock_settings, mock_run_command):
        """Test execute_git_commands with all operations disabled."""
        # Setup
        args = VersionArgs(
            version="1.0.0",
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
            path=".",
        )
        next_version = Version(1, 0, 0)

        # Execute
        execute_git_commands(args, next_version, 0)

        # Verify - should still call run_command with empty string
        mock_run_command.assert_called_once_with(mock_settings, "")


class TestPreReleaseAndCustomVersion:
    """Test cases for pre-release and custom version functions."""

    @patch("tgit.version.questionary")
    def test_get_pre_release_identifier_success(self, mock_questionary):
        """Test get_pre_release_identifier with valid input."""
        mock_text = Mock()
        mock_text.ask.return_value = "alpha.1"
        mock_questionary.text.return_value = mock_text

        result = get_pre_release_identifier()

        assert result == "alpha.1"
        mock_questionary.text.assert_called_once()

    @patch("tgit.version.questionary")
    def test_get_pre_release_identifier_cancel(self, mock_questionary):
        """Test get_pre_release_identifier when user cancels."""
        mock_text = Mock()
        mock_text.ask.return_value = None
        mock_questionary.text.return_value = mock_text

        result = get_pre_release_identifier()

        assert result is None

    @patch("tgit.version.questionary")
    def test_get_custom_version_success(self, mock_questionary):
        """Test get_custom_version with valid semver input."""
        mock_text = Mock()
        mock_text.ask.return_value = "2.5.0-beta.3"
        mock_questionary.text.return_value = mock_text

        result = get_custom_version()

        assert result is not None
        assert result.major == 2
        assert result.minor == 5
        assert result.patch == 0
        assert result.release == "beta.3"

    @patch("tgit.version.questionary")
    def test_get_custom_version_cancel(self, mock_questionary):
        """Test get_custom_version when user cancels."""
        mock_text = Mock()
        mock_text.ask.return_value = None
        mock_questionary.text.return_value = mock_text

        result = get_custom_version()

        assert result is None

    @patch("tgit.version.questionary")
    def test_get_custom_version_empty_string(self, mock_questionary):
        """Test get_custom_version when user enters empty string."""
        mock_text = Mock()
        mock_text.ask.return_value = ""
        mock_questionary.text.return_value = mock_text

        result = get_custom_version()

        assert result is None


class TestExplicitVersionArgs:
    """Test cases for explicit version argument handling."""

    def test_handle_explicit_version_args_preminor(self):
        """Test _handle_explicit_version_args with preminor."""
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
            preminor="rc",
            premajor="",
            recursive=False,
            custom="",
            path=".",
        )
        prev_version = Version(1, 2, 3)

        result = _handle_explicit_version_args(args, prev_version)

        assert result is not None
        assert result.major == 1
        assert result.minor == 3
        assert result.patch == 0
        assert result.release == "rc"

    def test_handle_explicit_version_args_premajor(self):
        """Test _handle_explicit_version_args with premajor."""
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
            premajor="beta",
            recursive=False,
            custom="",
            path=".",
        )
        prev_version = Version(1, 2, 3)

        result = _handle_explicit_version_args(args, prev_version)

        assert result is not None
        assert result.major == 2
        assert result.minor == 0
        assert result.patch == 0
        assert result.release == "beta"

    @patch("tgit.version.get_custom_version")
    def test_handle_explicit_version_args_custom(self, mock_get_custom_version):
        """Test _handle_explicit_version_args with custom."""
        mock_get_custom_version.return_value = Version(3, 0, 0, release="special")
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
            custom="custom",
            path=".",
        )
        prev_version = Version(1, 2, 3)

        result = _handle_explicit_version_args(args, prev_version)

        assert result is not None
        assert result.major == 3
        assert result.minor == 0
        assert result.patch == 0
        assert result.release == "special"
        mock_get_custom_version.assert_called_once()


class TestVersionApplyChoice:
    """Test cases for version choice application."""

    @patch("tgit.version.get_pre_release_identifier")
    def test_apply_version_choice_prepatch_with_release(self, mock_get_pre_release):
        """Test _apply_version_choice with prepatch when user provides release."""
        mock_get_pre_release.return_value = "alpha"
        target = VersionChoice(Version(1, 2, 3), "prepatch")
        prev_version = Version(1, 2, 3)

        result = _apply_version_choice(target, prev_version)

        assert result is not None
        assert result.major == 1
        assert result.minor == 2
        assert result.patch == 4
        assert result.release == "alpha"

    @patch("tgit.version.get_pre_release_identifier")
    def test_apply_version_choice_prepatch_cancelled(self, mock_get_pre_release):
        """Test _apply_version_choice with prepatch when user cancels."""
        mock_get_pre_release.return_value = None
        target = VersionChoice(Version(1, 2, 3), "prepatch")
        prev_version = Version(1, 2, 3)

        result = _apply_version_choice(target, prev_version)

        assert result is None

    @patch("tgit.version.get_custom_version")
    def test_apply_version_choice_custom_success(self, mock_get_custom_version):
        """Test _apply_version_choice with custom when user provides version."""
        mock_get_custom_version.return_value = Version(5, 0, 0)
        target = VersionChoice(Version(1, 2, 3), "custom")
        prev_version = Version(1, 2, 3)

        result = _apply_version_choice(target, prev_version)

        assert result is not None
        assert result.major == 5
        assert result.minor == 0
        assert result.patch == 0

    @patch("tgit.version.get_custom_version")
    def test_apply_version_choice_custom_cancelled(self, mock_get_custom_version):
        """Test _apply_version_choice with custom when user cancels."""
        mock_get_custom_version.return_value = None
        target = VersionChoice(Version(1, 2, 3), "custom")
        prev_version = Version(1, 2, 3)

        result = _apply_version_choice(target, prev_version)

        assert result is None


class TestVersionFileHandlingEdgeCases:
    """Test cases for version file handling edge cases."""

    def test_get_version_from_pyproject_toml_flit(self, tmp_path):
        """Test get_version_from_pyproject_toml with flit metadata."""
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[tool.flit.metadata]
version = "1.5.0"
""")

        result = get_version_from_pyproject_toml(tmp_path)

        assert result is not None
        assert result.major == 1
        assert result.minor == 5
        assert result.patch == 0

    def test_get_version_from_pyproject_toml_setuptools(self, tmp_path):
        """Test get_version_from_pyproject_toml with setuptools metadata."""
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[tool.setuptools.setup_requires]
version = "2.1.0"
""")

        result = get_version_from_pyproject_toml(tmp_path)

        assert result is not None
        assert result.major == 2
        assert result.minor == 1
        assert result.patch == 0

    @patch("tgit.version.console")
    def test_get_version_from_cargo_toml_file_read_error(self, mock_console, tmp_path):
        """Test get_version_from_cargo_toml with file read error."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text("valid content")
        cargo_toml.chmod(0o000)  # Remove read permissions

        try:
            result = get_version_from_cargo_toml(tmp_path)

            assert result is None
            mock_console.print.assert_called()
        finally:
            cargo_toml.chmod(0o644)  # Restore permissions for cleanup

    @patch("tgit.version.shutil.which")
    def test_get_version_from_git_no_executable(self, mock_which, tmp_path):
        """Test get_version_from_git when git executable is not found."""
        mock_which.return_value = None

        with pytest.raises(FileNotFoundError, match="Git executable not found"):
            get_version_from_git(tmp_path)


class TestCliCommand:
    """Test cases for the CLI command."""

    @patch("tgit.version.handle_version")
    def test_version_command_basic(self, mock_handle_version):
        """Test version command with basic parameters."""
        runner = CliRunner()
        result = runner.invoke(version, [])

        assert result.exit_code == 0
        mock_handle_version.assert_called_once()

    def test_version_command_mutually_exclusive_options(self):
        """Test version command with mutually exclusive options."""
        runner = CliRunner()
        result = runner.invoke(version, ["--patch", "--minor"])

        assert result.exit_code != 0
        assert "Only one version bump option can be specified" in result.output

    @patch("tgit.version.handle_version")
    def test_version_command_all_options(self, mock_handle_version):
        """Test version command with all available options."""
        runner = CliRunner()
        result = runner.invoke(version, ["--verbose", "--verbose", "--no-commit", "--no-tag", "--no-push", "--recursive", "--patch", "."])

        assert result.exit_code == 0
        mock_handle_version.assert_called_once()

        # Check that the VersionArgs object was created correctly
        args = mock_handle_version.call_args[0][0]
        assert args.verbose == 2
        assert args.no_commit is True
        assert args.no_tag is True
        assert args.no_push is True
        assert args.recursive is True
        assert args.patch is True


class TestRemainingEdgeCases:
    """Test cases for remaining edge cases to improve coverage."""

    def test_get_version_from_files_fallback_order(self, tmp_path):
        """Test get_version_from_files fallback order."""
        # Test setup.py fallback
        setup_py = tmp_path / "setup.py"
        setup_py.write_text('version="1.2.3"')

        result = get_version_from_files(tmp_path)
        assert result is not None
        assert str(result) == "1.2.3"

        # Test Cargo.toml fallback (when package.json doesn't exist)
        setup_py.unlink()
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text("""
[package]
name = "test"
version = "2.0.0"
""")

        result = get_version_from_files(tmp_path)
        assert result is not None
        assert str(result) == "2.0.0"

        # Test VERSION file fallback
        cargo_toml.unlink()
        version_file = tmp_path / "VERSION"
        version_file.write_text("3.0.0")

        result = get_version_from_files(tmp_path)
        assert result is not None
        assert str(result) == "3.0.0"

        # Test VERSION.txt fallback
        version_file.unlink()
        version_txt = tmp_path / "VERSION.txt"
        version_txt.write_text("4.0.0")

        result = get_version_from_files(tmp_path)
        assert result is not None
        assert str(result) == "4.0.0"

    @patch("tgit.version.subprocess.run")
    def test_get_version_from_git_with_tags(self, mock_run, tmp_path):
        """Test get_version_from_git with version tags."""
        # Mock successful git tag command with tags
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout.decode.return_value = "v1.0.0\nv1.1.0\nother-tag\nv2.0.0\n"
        mock_run.return_value = mock_result

        result = get_version_from_git(tmp_path)

        assert result is not None
        assert str(result) == "1.0.0"  # Should return first v-prefixed tag

    @patch("tgit.version.subprocess.run")
    def test_get_version_from_git_no_tags(self, mock_run, tmp_path):
        """Test get_version_from_git when no tags exist."""
        # Mock git tag command with no output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout.decode.return_value = ""
        mock_run.return_value = mock_result

        result = get_version_from_git(tmp_path)

        assert result is None

    @patch("tgit.version.subprocess.run")
    def test_get_version_from_git_command_failed(self, mock_run, tmp_path):
        """Test get_version_from_git when git command fails."""
        # Mock failed git tag command
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = get_version_from_git(tmp_path)

        assert result is None

    @patch("tgit.version.get_root_detected_files")
    @patch("tgit.version.console")
    def test_handle_version_no_files_detected(self, mock_console, mock_get_detected_files):
        """Test handle_version when no version files are detected."""
        # Setup
        mock_get_detected_files.return_value = []
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

        # Execute
        handle_version(args)

        # Verify
        mock_console.print.assert_any_call("No version files detected for update.")

    @patch("tgit.version.questionary")
    def test_handle_interactive_version_selection_cancel(self, mock_questionary):
        """Test _handle_interactive_version_selection when user cancels."""
        mock_select = Mock()
        mock_select.ask.return_value = None
        mock_questionary.select.return_value = mock_select

        prev_version = Version(1, 0, 0)
        result = _handle_interactive_version_selection(prev_version, "patch", 0)

        assert result is None

    def test_update_file_nonexistent(self, tmp_path):
        """Test update_file with non-existent file."""
        non_existent_file = tmp_path / "nonexistent.txt"

        # Should not raise error, just return early
        update_file(str(non_existent_file), r"old", "new", 0, show_diff=False)

        # File should still not exist
        assert not non_existent_file.exists()

    def test_update_cargo_toml_version_nonexistent(self, tmp_path):
        """Test update_cargo_toml_version with non-existent file."""
        non_existent_file = tmp_path / "Cargo.toml"

        # Should not raise error, just return early
        update_cargo_toml_version(str(non_existent_file), "1.0.0", 0, show_diff=False)

        # File should still not exist
        assert not non_existent_file.exists()

    @patch("tgit.version.Path.open")
    def test_parse_gitignore_unicode_decode_error(self, mock_open):
        """Test _parse_gitignore with UnicodeDecodeError."""
        mock_open.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "error")

        result = _parse_gitignore(Path("/fake/.gitignore"))

        assert result == []

    @patch("tgit.version.Path.open")
    def test_parse_gitignore_os_error(self, mock_open):
        """Test _parse_gitignore with OSError."""
        mock_open.side_effect = OSError("File not accessible")

        result = _parse_gitignore(Path("/fake/.gitignore"))

        assert result == []

    def test_get_root_detected_files(self, tmp_path):
        """Test get_root_detected_files functionality."""
        # Create test files
        package_json = tmp_path / "package.json"
        package_json.write_text('{"version": "1.0.0"}')

        version_file = tmp_path / "VERSION"
        version_file.write_text("2.0.0")

        # Test detection
        detected = get_root_detected_files(str(tmp_path))

        assert len(detected) == 2
        assert any(f.name == "package.json" for f in detected)
        assert any(f.name == "VERSION" for f in detected)

    @patch("tgit.version.update_version_in_file")
    @patch("tgit.version.get_detected_files")
    @patch("tgit.version.console")
    def test_update_version_files_verbose_mode(self, mock_console, mock_get_detected_files, mock_update_version_in_file):
        """Test update_version_files in verbose mode."""
        mock_detected_file = Mock()
        mock_detected_file.name = "package.json"
        mock_get_detected_files.return_value = [mock_detected_file]

        args = VersionArgs(
            version="",
            verbose=1,
            no_commit=False,
            no_tag=False,
            no_push=False,
            patch=False,
            minor=False,
            major=False,
            prepatch="",
            preminor="",
            premajor="",
            recursive=True,
            custom="",
            path="/test",
        )
        next_version = Version(2, 0, 0)

        update_version_files(args, next_version, 1, reclusive=True)

        # Check verbose output
        mock_console.print.assert_any_call("Current path: [cyan bold]/test")

    def test_update_version_in_file_setup_py(self, tmp_path):
        """Test update_version_in_file with setup.py file."""
        setup_py = tmp_path / "setup.py"
        setup_py.write_text('version="1.0.0"')

        update_version_in_file(0, "2.0.0", "setup.py", setup_py, show_diff=False)

        content = setup_py.read_text()
        assert "version='2.0.0'" in content

    def test_update_version_in_file_build_gradle_kts(self, tmp_path):
        """Test update_version_in_file with build.gradle.kts file."""
        build_file = tmp_path / "build.gradle.kts"
        build_file.write_text('version = "1.0.0"')

        update_version_in_file(0, "2.0.0", "build.gradle.kts", build_file, show_diff=False)

        content = build_file.read_text()
        assert 'version = "2.0.0"' in content

    @patch("tgit.version.questionary")
    @patch("tgit.version.sys.exit")
    def test_show_file_diff_user_exits(self, mock_exit, mock_questionary):
        """Test show_file_diff when user chooses to exit."""
        mock_confirm = Mock()
        mock_confirm.ask.return_value = False
        mock_questionary.confirm.return_value = mock_confirm

        show_file_diff("old content\n", "new content\n", "test.txt")

        mock_exit.assert_called_once()

    def test_format_diff_lines_with_question_mark(self):
        """Test format_diff_lines with question mark lines."""
        diff = ["? ^^", "- old line", "+ new line"]
        print_lines = {0: "?", 1: "-", 2: "+"}
        diffs = []

        format_diff_lines(diff, print_lines, diffs)

        assert len(diffs) == 3
        assert "[yellow]" in diffs[0]
        assert "[red]" in diffs[1]
        assert "[green]" in diffs[2]
