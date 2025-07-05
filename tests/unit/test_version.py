from unittest.mock import Mock, patch

import pytest

from tgit.version import (
    Version,
    VersionArgs,
    VersionChoice,
    _apply_version_choice,
    _get_default_bump_from_commits,
    _handle_explicit_version_args,
    _handle_interactive_version_selection,
    _has_explicit_version_args,
    _prompt_for_version_choice,
    bump_version,
    get_default_bump_by_commits_dict,
    get_next_version,
    get_version_from_cargo_toml,
    get_version_from_files,
    get_version_from_package_json,
    get_version_from_pyproject_toml,
    get_version_from_setup_py,
    get_version_from_version_file,
    get_version_from_version_txt,
    show_file_diff,
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
