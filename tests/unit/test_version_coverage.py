import re
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from tgit.version import (
    Version,
    VersionArgs,
    VersionChoice,
    _apply_version_choice,
    _get_default_bump_from_commits,
    _handle_interactive_version_selection,
    _should_ignore_path,
    get_custom_version,
    get_version_from_build_gradle_kts,
    get_version_from_cargo_toml,
    get_version_from_git,
    get_version_from_pyproject_toml,
    get_version_from_setup_py,
    get_version_from_version_file,
    get_version_from_version_txt,
    handle_version,
    update_cargo_toml_version,
    update_file,
    update_file_in_root,
    update_version_in_file,
)


class TestVersionCoverage:
    """Additional tests to increase coverage for version.py."""

    def test_get_version_from_build_gradle_kts(self, tmp_path):
        """Test extracting version from build.gradle.kts."""
        gradle_file = tmp_path / "build.gradle.kts"
        gradle_file.write_text('version = "1.2.3"')

        version = get_version_from_build_gradle_kts(tmp_path)
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_get_version_from_build_gradle_kts_invalid(self, tmp_path):
        """Test extracting invalid version from build.gradle.kts."""
        gradle_file = tmp_path / "build.gradle.kts"
        gradle_file.write_text('version = "invalid"')

        version = get_version_from_build_gradle_kts(tmp_path)
        assert version is None

    def test_get_version_from_build_gradle_kts_missing(self, tmp_path):
        """Test extracting version from missing build.gradle.kts."""
        version = get_version_from_build_gradle_kts(tmp_path)
        assert version is None

    def test_get_version_from_pyproject_toml_value_error(self, tmp_path):
        """Test ValueError handling in get_version_from_pyproject_toml."""
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[project]
version = "invalid"
""")
        version = get_version_from_pyproject_toml(tmp_path)
        assert version is None

    def test_get_version_from_setup_py_value_error(self, tmp_path):
        """Test ValueError handling in get_version_from_setup_py."""
        setup_py = tmp_path / "setup.py"
        setup_py.write_text("version='invalid'")
        version = get_version_from_setup_py(tmp_path)
        assert version is None

    def test_get_version_from_cargo_toml_value_error(self, tmp_path):
        """Test ValueError handling in get_version_from_cargo_toml."""
        cargo_toml = tmp_path / "Cargo.toml"
        cargo_toml.write_text("""
[package]
name = "test"
version = "invalid"
""")
        version = get_version_from_cargo_toml(tmp_path)
        assert version is None

    def test_get_version_from_version_file_value_error(self, tmp_path):
        """Test ValueError handling in get_version_from_version_file."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("invalid")
        version = get_version_from_version_file(tmp_path)
        assert version is None

    def test_get_version_from_version_txt_value_error(self, tmp_path):
        """Test ValueError handling in get_version_from_version_txt."""
        version_txt = tmp_path / "VERSION.txt"
        version_txt.write_text("invalid")
        version = get_version_from_version_txt(tmp_path)
        assert version is None

    @patch("tgit.version.shutil.which")
    @patch("tgit.version.subprocess.run")
    def test_get_version_from_git_value_error(self, mock_run, mock_which, tmp_path):
        """Test ValueError handling in get_version_from_git."""
        mock_which.return_value = "/usr/bin/git"
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b"vinvalid\n"

        version = get_version_from_git(tmp_path)
        assert version is None

    def test_should_ignore_path_parent_match(self):
        """Test _should_ignore_path when a parent directory matches."""
        root = Path("/root")
        path = Path("/root/ignored_parent/child/file.txt")
        patterns = ["ignored_parent/"]
        assert _should_ignore_path(path, root, patterns) is True

    @patch("tgit.version.get_current_version")
    @patch("tgit.version.get_next_version")
    @patch("tgit.version.questionary.confirm")
    @patch("tgit.version.handle_changelog")
    @patch("tgit.version.update_version_files")
    @patch("tgit.version.execute_git_commands")
    def test_handle_version_with_changelog(
        self,
        mock_execute,
        mock_update,
        mock_changelog,
        mock_confirm,
        mock_get_next,
        mock_get_current,
        tmp_path,
    ):
        """Test handle_version with changelog generation."""
        # Create a version file so it doesn't return early
        (tmp_path / "package.json").write_text("{}")

        mock_get_current.return_value = Version(1, 0, 0)
        mock_get_next.return_value = Version(1, 1, 0)
        mock_confirm.return_value.ask.return_value = True

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
            recursive=False,
            custom="",
            path=str(tmp_path),
        )

        handle_version(args)

        mock_changelog.assert_called_once()
        call_args = mock_changelog.call_args
        assert call_args[0][0].output == "CHANGELOG.md"
        assert call_args[1]["current_tag"] == "v1.1.0"

    def test_get_version_from_files_gradle(self, tmp_path):
        """Test get_version_from_files with build.gradle.kts."""
        gradle_file = tmp_path / "build.gradle.kts"
        gradle_file.write_text('version = "1.2.3"')
        
        # Ensure other files don't exist
        from tgit.version import get_version_from_files
        version = get_version_from_files(tmp_path)
        
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_should_ignore_path_parent_match_no_slash(self):
        """Test _should_ignore_path when a parent directory matches pattern without slash."""
        root = Path("/root")
        path = Path("/root/ignored_parent/child/file.txt")
        patterns = ["ignored_parent"]
        assert _should_ignore_path(path, root, patterns) is True

    @patch("tgit.version.bump_version")
    def test_apply_version_choice_regular(self, mock_bump):
        """Test _apply_version_choice with regular bump."""
        prev_version = Version(1, 0, 0)
        target = VersionChoice(prev_version, "patch")
        
        _apply_version_choice(target, prev_version)
        
        mock_bump.assert_called_once()

    @patch("tgit.version.git.Repo")
    @patch("tgit.version.get_git_commits_range")
    @patch("tgit.version.get_commits")
    @patch("tgit.version.group_commits_by_type")
    @patch("tgit.version.console")
    def test_get_default_bump_from_commits_verbose(
        self,
        mock_console,
        mock_group,
        mock_get_commits,
        mock_get_range,
        mock_repo,
    ):
        """Test _get_default_bump_from_commits with verbose output."""
        mock_repo.return_value = Mock()
        mock_get_range.return_value = ("HEAD~1", "HEAD")
        mock_get_commits.return_value = []
        mock_group.return_value = {}

        _get_default_bump_from_commits(".", Version(1, 0, 0), verbose=1)

        mock_console.print.assert_any_call("Getting commits...")

    @patch("tgit.version._prompt_for_version_choice")
    @patch("tgit.version._apply_version_choice")
    @patch("tgit.version.console")
    def test_handle_interactive_version_selection_verbose(
        self,
        mock_console,
        mock_apply,
        mock_prompt,
    ):
        """Test _handle_interactive_version_selection with verbose output."""
        prev_version = Version(1, 0, 0)
        choice = VersionChoice(prev_version, "patch")
        mock_prompt.return_value = choice
        mock_apply.return_value = Version(1, 0, 1)

        _handle_interactive_version_selection(prev_version, "patch", verbose=1)

        mock_console.print.assert_any_call(f"Selected target: [cyan bold]{choice}")

    def test_apply_version_choice_release(self):
        """Test _apply_version_choice with release bump."""
        prev_version = Version(1, 0, 0, release="beta")
        target = VersionChoice(prev_version, "release")
        
        next_version = _apply_version_choice(target, prev_version)
        
        assert next_version.release is None
        assert next_version.major == 1
        assert next_version.minor == 0
        assert next_version.patch == 0

    @patch("tgit.version.questionary.text")
    def test_get_custom_version_validation(self, mock_text):
        """Test get_custom_version validation logic."""
        mock_ask = mock_text.return_value.ask
        mock_ask.return_value = "1.2.3"
        
        get_custom_version()
        
        # Check validation function
        validate = mock_text.call_args[1]["validate"]
        assert validate("1.2.3") is True
        assert validate("invalid") is False

    @patch("tgit.version.update_cargo_toml_version")
    def test_update_version_in_file_cargo(self, mock_update, tmp_path):
        """Test update_version_in_file for Cargo.toml."""
        file_path = tmp_path / "Cargo.toml"
        update_version_in_file(0, "1.2.3", "Cargo.toml", file_path)
        mock_update.assert_called_once()

    @patch("tgit.version.update_file")
    @patch("tgit.version.update_cargo_toml_version")
    def test_update_file_in_root(self, mock_update_cargo, mock_update_file, tmp_path):
        """Test update_file_in_root."""
        update_file_in_root("1.2.3", 0, tmp_path)
        
        assert mock_update_file.call_count == 6  # package.json, pyproject.toml, setup.py, build.gradle.kts, VERSION, VERSION.txt
        mock_update_cargo.assert_called_once()

    @patch("tgit.version.console")
    @patch("tgit.version.show_file_diff")
    def test_update_file_verbose_and_diff(self, mock_show_diff, mock_console, tmp_path):
        """Test update_file with verbose and show_diff."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("old")
        
        update_file(str(file_path), None, "new", verbose=1, show_diff=True)
        
        mock_console.print.assert_called_with(f"Updating {file_path}")
        mock_show_diff.assert_called_once()
        assert file_path.read_text() == "new"

    @patch("tgit.version.console")
    @patch("tgit.version.show_file_diff")
    def test_update_cargo_toml_version_verbose_and_diff(self, mock_show_diff, mock_console, tmp_path):
        """Test update_cargo_toml_version with verbose and show_diff."""
        file_path = tmp_path / "Cargo.toml"
        file_path.write_text('[package]\nversion = "0.1.0"')
        
        update_cargo_toml_version(str(file_path), "0.2.0", verbose=1, show_diff=True)
        
        mock_console.print.assert_called_with(f"Updating {file_path}")
        mock_show_diff.assert_called_once()
        assert 'version = "0.2.0"' in file_path.read_text()
