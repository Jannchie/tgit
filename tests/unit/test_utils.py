import json
import pytest
from unittest.mock import patch, MagicMock
import subprocess
import sys

from tgit.utils import run_command, simple_run_command, get_commit_command, type_emojis, load_workspace_settings
from tgit.types import TGitSettings, CommitSettings


class TestRunCommand:
    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.questionary.confirm")
    def test_run_command_user_confirms(self, mock_confirm, mock_popen):
        """Test run_command when user confirms execution."""
        # Arrange
        mock_confirm.return_value.ask.return_value = True
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"output", b"")
        process_mock.returncode = 0
        settings = TGitSettings(
            commit=CommitSettings(emoji=False, types=[]), api_key="", api_url="", model="", show_command=False, skip_confirm=False
        )

        # Act
        run_command(settings, "echo 'test'")

        # Assert
        mock_confirm.assert_called_once_with("Do you want to continue?", default=True)
        mock_popen.assert_called_once()

    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.questionary.confirm")
    def test_run_command_user_cancels(self, mock_confirm, mock_popen):
        """Test run_command when user cancels execution."""
        # Arrange
        mock_confirm.return_value.ask.return_value = False
        settings = TGitSettings(
            commit=CommitSettings(emoji=False, types=[]), api_key="", api_url="", model="", show_command=False, skip_confirm=False
        )

        # Act
        run_command(settings, "echo 'test'")

        # Assert
        mock_confirm.assert_called_once_with("Do you want to continue?", default=True)
        mock_popen.assert_not_called()

    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.questionary.confirm")
    def test_run_command_skip_confirm(self, mock_confirm, mock_popen):
        """Test run_command when skip_confirm is True."""
        # Arrange
        settings = TGitSettings(
            commit=CommitSettings(emoji=False, types=[]), api_key="", api_url="", model="", show_command=False, skip_confirm=True
        )
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"output", b"")
        process_mock.returncode = 0

        # Act
        run_command(settings, "echo 'test'")

        # Assert
        mock_confirm.assert_not_called()
        mock_popen.assert_called_once()

    @patch("tgit.utils.console.print")
    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.questionary.confirm")
    def test_run_command_show_command(self, mock_confirm, mock_popen, mock_console_print):
        """Test run_command when show_command is True."""
        # Arrange
        settings = TGitSettings(
            commit=CommitSettings(emoji=False, types=[]), api_key="", api_url="", model="", show_command=True, skip_confirm=False
        )
        mock_confirm.return_value.ask.return_value = True
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"output", b"")
        process_mock.returncode = 0

        # Act
        run_command(settings, "echo 'test'")

        # Assert
        assert mock_console_print.call_count >= 1
        mock_confirm.assert_called_once()
        mock_popen.assert_called_once()

    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.questionary.confirm")
    @patch("tgit.utils.sys.stderr.write")
    def test_run_command_error_handling(self, mock_stderr_write, mock_confirm, mock_popen):
        """Test run_command error handling."""
        # Arrange
        settings = TGitSettings(
            commit=CommitSettings(emoji=False, types=[]), api_key="", api_url="", model="", show_command=False, skip_confirm=True
        )
        mock_confirm.return_value.ask.return_value = True
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"", b"error message")
        process_mock.returncode = 1

        # Act
        run_command(settings, "failing command")

        # Assert
        mock_stderr_write.assert_called_once_with("error message")

    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.questionary.confirm")
    def test_run_command_multiple_commands(self, mock_confirm, mock_popen):
        """Test run_command with multiple commands."""
        # Arrange
        settings = TGitSettings(
            commit=CommitSettings(emoji=False, types=[]), api_key="", api_url="", model="", show_command=False, skip_confirm=True
        )
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"output", b"")
        process_mock.returncode = 0

        # Act
        run_command(settings, "echo 'first'\necho 'second'")

        # Assert
        assert mock_popen.call_count == 2


class TestSimpleRunCommand:
    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.sys.stdout.write")
    def test_simple_run_command_success(self, mock_stdout_write, mock_popen):
        """Test simple_run_command with successful execution."""
        # Arrange
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"output", b"")
        process_mock.returncode = 0

        # Act
        simple_run_command("echo 'test'")

        # Assert
        mock_popen.assert_called_once_with("echo 'test'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # noqa: S604
        mock_stdout_write.assert_called_once_with("output")

    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.sys.stderr.write")
    def test_simple_run_command_error(self, mock_stderr_write, mock_popen):
        """Test simple_run_command with error."""
        # Arrange
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"", b"error message")
        process_mock.returncode = 1

        # Act
        simple_run_command("failing command")

        # Assert
        mock_stderr_write.assert_called_once_with("error message")

    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.sys.stderr.write")
    @patch("tgit.utils.sys.stdout.write")
    def test_simple_run_command_no_output(self, mock_stdout_write, mock_stderr_write, mock_popen):
        """Test simple_run_command with no output."""
        # Arrange
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"", b"")
        process_mock.returncode = 0

        # Act
        simple_run_command("silent command")

        # Assert
        mock_stdout_write.assert_not_called()
        mock_stderr_write.assert_not_called()


class TestGetCommitCommand:
    def test_get_commit_command_basic(self):
        """Test basic commit command generation."""
        result = get_commit_command("feat", None, "add new feature")
        assert result == 'git commit -m "feat: add new feature"'

    def test_get_commit_command_with_scope(self):
        """Test commit command with scope."""
        result = get_commit_command("fix", "auth", "fix login issue")
        assert result == 'git commit -m "fix(auth): fix login issue"'

    def test_get_commit_command_with_emoji(self):
        """Test commit command with emoji."""
        result = get_commit_command("feat", None, "add new feature", use_emoji=True)
        assert result == 'git commit -m ":sparkles: feat: add new feature"'

    def test_get_commit_command_with_emoji_and_scope(self):
        """Test commit command with emoji and scope."""
        result = get_commit_command("fix", "api", "fix endpoint", use_emoji=True)
        assert result == 'git commit -m ":adhesive_bandage: fix(api): fix endpoint"'

    def test_get_commit_command_breaking_change(self):
        """Test commit command with breaking change."""
        result = get_commit_command("feat", None, "breaking change", is_breaking=True)
        assert result == 'git commit -m "feat!: breaking change"'

    def test_get_commit_command_breaking_change_with_scope(self):
        """Test commit command with breaking change and scope."""
        result = get_commit_command("feat", "api", "breaking change", is_breaking=True)
        assert result == 'git commit -m "feat(api)!: breaking change"'

    def test_get_commit_command_breaking_change_with_emoji(self):
        """Test commit command with breaking change and emoji."""
        result = get_commit_command("feat", None, "breaking change", use_emoji=True, is_breaking=True)
        assert result == 'git commit -m ":sparkles: feat!: breaking change"'

    def test_get_commit_command_type_with_exclamation(self):
        """Test commit command when type already has exclamation."""
        result = get_commit_command("feat!", None, "breaking change")
        assert result == 'git commit -m "feat!: breaking change"'

    def test_get_commit_command_type_with_exclamation_and_scope(self):
        """Test commit command when type has exclamation and scope."""
        result = get_commit_command("feat!", "api", "breaking change")
        assert result == 'git commit -m "feat(api)!: breaking change"'

    def test_get_commit_command_unknown_type_emoji(self):
        """Test commit command with unknown type gets default emoji."""
        result = get_commit_command("custom", None, "custom change", use_emoji=True)
        assert result == 'git commit -m ":wrench: custom: custom change"'

    def test_get_commit_command_all_commit_types(self):
        """Test commit command with all known commit types."""
        for commit_type, emoji in type_emojis.items():
            result = get_commit_command(commit_type, None, "test message", use_emoji=True)
            expected = f'git commit -m "{emoji} {commit_type}: test message"'
            assert result == expected


class TestTypeEmojis:
    def test_type_emojis_complete(self):
        """Test that all expected commit types have emojis."""
        expected_types = ["feat", "fix", "chore", "docs", "style", "refactor", "perf", "test", "version", "ci"]
        for commit_type in expected_types:
            assert commit_type in type_emojis
            assert type_emojis[commit_type].startswith(":")
            assert type_emojis[commit_type].endswith(":")


class TestSettingsFileHandling:
    """Test settings file loading and error handling."""

    def test_load_settings_basic_functionality(self, tmp_path):
        """Test basic settings file loading."""
        # Create .tgit directory and settings.json file
        tgit_dir = tmp_path / ".tgit"
        tgit_dir.mkdir()
        config_file = tgit_dir / "settings.json"
        config_file.write_text(json.dumps({"apiKey": "test_key", "model": "gpt-4"}))

        with patch("tgit.utils.Path.cwd", return_value=tmp_path):
            result = load_workspace_settings()

            assert result["apiKey"] == "test_key"
            assert result["model"] == "gpt-4"
