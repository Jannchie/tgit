"""Tests for interactive_settings module."""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from tgit.interactive_settings import (
    interactive_settings,
    _view_current_settings,
    _configure_global_settings,
    _configure_workspace_settings,
    _reset_settings,
    _configure_commit_types,
)


class TestInteractiveSettings:
    """Test interactive_settings function."""

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.print")
    def test_interactive_settings_exit(self, mock_print, mock_select):
        """Test interactive_settings with exit choice."""
        mock_select.return_value.ask.return_value = "exit"

        interactive_settings()

        mock_print.assert_any_call("[bold blue]TGIT Interactive Settings[/bold blue]")
        mock_print.assert_any_call("Configure your TGIT settings interactively.")
        mock_select.assert_called_once()

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.print")
    def test_interactive_settings_cancel(self, mock_print, mock_select):
        """Test interactive_settings with cancel (None) choice."""
        mock_select.return_value.ask.return_value = None

        interactive_settings()

        mock_select.assert_called_once()

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings._view_current_settings")
    @patch("tgit.interactive_settings.print")
    def test_interactive_settings_view(self, mock_print, mock_view, mock_select):
        """Test interactive_settings with view choice."""
        mock_select.return_value.ask.side_effect = ["view", "exit"]

        interactive_settings()

        mock_view.assert_called_once()
        assert mock_select.call_count == 2

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings._configure_global_settings")
    @patch("tgit.interactive_settings.print")
    def test_interactive_settings_global(self, mock_print, mock_global, mock_select):
        """Test interactive_settings with global config choice."""
        mock_select.return_value.ask.side_effect = ["global", "exit"]

        interactive_settings()

        mock_global.assert_called_once()
        assert mock_select.call_count == 2

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings._configure_workspace_settings")
    @patch("tgit.interactive_settings.print")
    def test_interactive_settings_workspace(self, mock_print, mock_workspace, mock_select):
        """Test interactive_settings with workspace config choice."""
        mock_select.return_value.ask.side_effect = ["workspace", "exit"]

        interactive_settings()

        mock_workspace.assert_called_once()
        assert mock_select.call_count == 2

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings._reset_settings")
    @patch("tgit.interactive_settings.print")
    def test_interactive_settings_reset(self, mock_print, mock_reset, mock_select):
        """Test interactive_settings with reset choice."""
        mock_select.return_value.ask.side_effect = ["reset", "exit"]

        interactive_settings()

        mock_reset.assert_called_once()
        assert mock_select.call_count == 2


class TestViewCurrentSettings:
    """Test _view_current_settings function."""

    @patch("tgit.interactive_settings.load_global_settings")
    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.print")
    @patch("builtins.input")
    @patch("tgit.interactive_settings.json.dumps")
    def test_view_current_settings_empty(self, mock_dumps, mock_input, mock_print, mock_workspace, mock_global):
        """Test _view_current_settings with empty settings."""
        mock_global.return_value = {}
        mock_workspace.return_value = {}
        mock_input.return_value = ""

        _view_current_settings()

        mock_print.assert_any_call("\n[bold green]Current Settings:[/bold green]")
        mock_print.assert_any_call("No global settings found")
        mock_print.assert_any_call("No workspace settings found")
        mock_global.assert_called_once()
        mock_workspace.assert_called_once()
        mock_input.assert_called_once()

    @patch("tgit.interactive_settings.load_global_settings")
    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.print")
    @patch("builtins.input")
    @patch("tgit.interactive_settings.json.dumps")
    def test_view_current_settings_with_data(self, mock_dumps, mock_input, mock_print, mock_workspace, mock_global):
        """Test _view_current_settings with actual settings."""
        mock_global.return_value = {"apiKey": "global-key", "model": "gpt-4"}
        mock_workspace.return_value = {"apiKey": "workspace-key"}
        mock_dumps.side_effect = ['{"apiKey": "global-key", "model": "gpt-4"}', '{"apiKey": "workspace-key"}']
        mock_input.return_value = ""

        _view_current_settings()

        mock_print.assert_any_call("\n[bold green]Current Settings:[/bold green]")
        mock_global.assert_called_once()
        mock_workspace.assert_called_once()
        mock_input.assert_called_once()


class TestConfigureGlobalSettings:
    """Test _configure_global_settings function."""

    @patch("tgit.interactive_settings.load_global_settings")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_global_settings_cancel_api_key(self, mock_text, mock_load):
        """Test _configure_global_settings with cancel at API key."""
        mock_load.return_value = {}
        mock_text.return_value.ask.return_value = None

        _configure_global_settings()

        mock_text.assert_called_once()

    @patch("tgit.interactive_settings.load_global_settings")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_global_settings_cancel_api_url(self, mock_text, mock_load):
        """Test _configure_global_settings with cancel at API URL."""
        mock_load.return_value = {}
        mock_text.return_value.ask.side_effect = ["api-key", None]

        _configure_global_settings()

        assert mock_text.call_count == 2

    @patch("tgit.interactive_settings.load_global_settings")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_global_settings_cancel_model(self, mock_text, mock_load):
        """Test _configure_global_settings with cancel at model."""
        mock_load.return_value = {}
        mock_text.return_value.ask.side_effect = ["api-key", "api-url", None]

        _configure_global_settings()

        assert mock_text.call_count == 3

    @patch("tgit.interactive_settings.load_global_settings")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_configure_global_settings_cancel_show_command(self, mock_confirm, mock_text, mock_load):
        """Test _configure_global_settings with cancel at show_command."""
        mock_load.return_value = {}
        mock_text.return_value.ask.side_effect = ["api-key", "api-url", "model"]
        mock_confirm.return_value.ask.return_value = None

        _configure_global_settings()

        mock_confirm.assert_called_once()

    @patch("tgit.interactive_settings.load_global_settings")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_configure_global_settings_cancel_skip_confirm(self, mock_confirm, mock_text, mock_load):
        """Test _configure_global_settings with cancel at skip_confirm."""
        mock_load.return_value = {}
        mock_text.return_value.ask.side_effect = ["api-key", "api-url", "model"]
        mock_confirm.return_value.ask.side_effect = [True, None]

        _configure_global_settings()

        assert mock_confirm.call_count == 2

    @patch("tgit.interactive_settings.load_global_settings")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_configure_global_settings_cancel_commit_emoji(self, mock_confirm, mock_text, mock_load):
        """Test _configure_global_settings with cancel at commit_emoji."""
        mock_load.return_value = {}
        mock_text.return_value.ask.side_effect = ["api-key", "api-url", "model"]
        mock_confirm.return_value.ask.side_effect = [True, False, None]

        _configure_global_settings()

        assert mock_confirm.call_count == 3

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.json.loads")
    @patch("tgit.interactive_settings.Path.home")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.load_global_settings")
    def test_configure_global_settings_complete(
        self, mock_load_global_settings, mock_text, mock_confirm, mock_home, mock_loads, mock_dumps, mock_write_text, mock_mkdir
    ):
        """Test _configure_global_settings complete flow."""
        mock_loads.return_value = {}
        mock_home.return_value = Path("/home/user")

        # Mock all questionary inputs
        mock_text.return_value.ask.side_effect = [
            "test-api-key",  # API key
            "https://api.example.com",  # API URL
            "gpt-4.1",  # model
        ]
        mock_confirm.return_value.ask.side_effect = [
            True,  # show_command
            False,  # skip_confirm
            True,  # commit_emoji
            False,  # configure_commit_types
        ]

        with patch("tgit.interactive_settings.load_global_settings", return_value={}):
            _configure_global_settings()

        # Verify all inputs were called
        assert mock_text.call_count == 3
        assert mock_confirm.call_count == 4
        mock_mkdir.assert_called_once()
        mock_write_text.assert_called_once()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.Path.home")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings._configure_commit_types")
    @patch("tgit.interactive_settings.load_global_settings")
    @patch("tgit.interactive_settings.print")
    def test_configure_global_settings_with_custom_commit_types(
        self,
        mock_print,
        mock_load_global_settings,
        mock_config_types,
        mock_text,
        mock_confirm,
        mock_home,
        mock_dumps,
        mock_write_text,
        mock_mkdir,
    ):
        """Test _configure_global_settings with custom commit types."""
        mock_home.return_value = Path("/home/user")
        mock_config_types.return_value = [{"type": "feat", "emoji": "✨"}]

        # Mock all questionary inputs
        mock_text.return_value.ask.side_effect = [
            "test-api-key",  # API key
            "",  # API URL (empty)
            "gpt-4.1",  # model
        ]
        mock_confirm.return_value.ask.side_effect = [
            True,  # show_command
            False,  # skip_confirm
            True,  # commit_emoji
            True,  # configure_commit_types
        ]

        with patch("tgit.interactive_settings.load_global_settings", return_value={}):
            _configure_global_settings()

        mock_config_types.assert_called_once()
        mock_print.assert_any_call("[green]Global settings saved successfully![/green]")


class TestConfigureWorkspaceSettings:
    """Test _configure_workspace_settings function."""

    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_configure_workspace_settings_decline_setup(self, mock_confirm, mock_load):
        """Test _configure_workspace_settings with decline setup."""
        mock_load.return_value = {}
        mock_confirm.return_value.ask.return_value = False

        _configure_workspace_settings()

        mock_confirm.assert_called_once()

    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_workspace_settings_cancel_api_key(self, mock_text, mock_confirm, mock_load):
        """Test _configure_workspace_settings with cancel at API key."""
        mock_load.return_value = {}
        mock_confirm.return_value.ask.return_value = True
        mock_text.return_value.ask.return_value = None

        _configure_workspace_settings()

        mock_text.assert_called_once()

    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_workspace_settings_cancel_api_url(self, mock_text, mock_confirm, mock_load):
        """Test _configure_workspace_settings with cancel at API URL."""
        mock_load.return_value = {}
        mock_confirm.return_value.ask.return_value = True
        mock_text.return_value.ask.side_effect = ["api-key", None]

        _configure_workspace_settings()

        assert mock_text.call_count == 2

    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_workspace_settings_cancel_model(self, mock_text, mock_confirm, mock_load):
        """Test _configure_workspace_settings with cancel at model."""
        mock_load.return_value = {}
        mock_confirm.return_value.ask.side_effect = [True, None]  # First confirm setup, then cancel at model
        mock_text.return_value.ask.side_effect = ["api-key", "api-url", None]

        _configure_workspace_settings()

        assert mock_text.call_count == 3

    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_workspace_settings_cancel_show_command(self, mock_text, mock_confirm, mock_load):
        """Test _configure_workspace_settings with cancel at show_command."""
        mock_load.return_value = {}
        mock_confirm.return_value.ask.side_effect = [True, None]  # Setup, then cancel at show_command
        mock_text.return_value.ask.side_effect = ["api-key", "api-url", "model"]

        _configure_workspace_settings()

        assert mock_text.call_count == 3
        assert mock_confirm.call_count == 2

    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_workspace_settings_cancel_skip_confirm(self, mock_text, mock_confirm, mock_load):
        """Test _configure_workspace_settings with cancel at skip_confirm."""
        mock_load.return_value = {}
        mock_confirm.return_value.ask.side_effect = [True, True, None]  # Setup, show_command, then cancel
        mock_text.return_value.ask.side_effect = ["api-key", "api-url", "model"]

        _configure_workspace_settings()

        assert mock_confirm.call_count == 3

    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_workspace_settings_cancel_commit_emoji(self, mock_text, mock_confirm, mock_load):
        """Test _configure_workspace_settings with cancel at commit_emoji."""
        mock_load.return_value = {}
        mock_confirm.return_value.ask.side_effect = [True, True, False, None]  # Setup, show_command, skip_confirm, then cancel
        mock_text.return_value.ask.side_effect = ["api-key", "api-url", "model"]

        _configure_workspace_settings()

        assert mock_confirm.call_count == 4

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.print")
    def test_configure_workspace_settings_complete_with_all_values(
        self, mock_print, mock_text, mock_confirm, mock_load, mock_dumps, mock_write_text, mock_mkdir
    ):
        """Test _configure_workspace_settings complete flow with all values."""
        mock_load.return_value = {}

        # Mock all inputs
        mock_text.return_value.ask.side_effect = ["workspace-api-key", "https://workspace-api.example.com", "gpt-4-workspace"]
        mock_confirm.return_value.ask.side_effect = [
            True,  # setup confirmation
            True,  # show_command
            True,  # skip_confirm
            False,  # commit_emoji
        ]

        _configure_workspace_settings()

        # Verify all calls were made
        assert mock_text.call_count == 3
        assert mock_confirm.call_count == 4
        mock_mkdir.assert_called_once()
        mock_write_text.assert_called_once()
        mock_print.assert_any_call(f"[green]Workspace settings saved to {Path.cwd() / '.tgit' / 'settings.json'}![/green]")

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.print")
    def test_configure_workspace_settings_complete_with_empty_values(
        self, mock_print, mock_text, mock_confirm, mock_load, mock_dumps, mock_write_text, mock_mkdir
    ):
        """Test _configure_workspace_settings complete flow with empty API values."""
        mock_load.return_value = {}

        # Mock all inputs with empty API values
        mock_text.return_value.ask.side_effect = [
            "",  # empty api key
            "",  # empty api url
            "",  # empty model
        ]
        mock_confirm.return_value.ask.side_effect = [
            True,  # setup confirmation
            False,  # show_command
            False,  # skip_confirm
            True,  # commit_emoji
        ]

        _configure_workspace_settings()

        # Verify all calls were made
        assert mock_text.call_count == 3
        assert mock_confirm.call_count == 4
        mock_mkdir.assert_called_once()
        mock_write_text.assert_called_once()


class TestResetSettings:
    """Test _reset_settings function."""

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.print")
    def test_reset_settings_cancel(self, mock_print, mock_select):
        """Test _reset_settings with cancel."""
        mock_select.return_value.ask.return_value = None

        _reset_settings()

        mock_print.assert_not_called()

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.Path.home")
    @patch("tgit.interactive_settings.print")
    def test_reset_settings_global_confirmed(self, mock_print, mock_home, mock_confirm, mock_select):
        """Test _reset_settings for global settings with confirmation."""
        mock_select.return_value.ask.return_value = "global"
        mock_confirm.return_value.ask.return_value = True
        mock_home.return_value = Path("/home/user")

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.unlink") as mock_unlink,
        ):
            _reset_settings()

            mock_confirm.assert_called_once()
            mock_unlink.assert_called_once()
            mock_print.assert_any_call("[green]Global settings reset successfully![/green]")

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.Path.home")
    @patch("tgit.interactive_settings.print")
    def test_reset_settings_global_cancelled(self, mock_print, mock_home, mock_confirm, mock_select):
        """Test _reset_settings for global settings cancelled."""
        mock_select.return_value.ask.return_value = "global"
        mock_confirm.return_value.ask.return_value = False
        mock_home.return_value = Path("/home/user")

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.unlink") as mock_unlink,
        ):
            _reset_settings()

            mock_confirm.assert_called_once()
            mock_unlink.assert_not_called()
            mock_print.assert_any_call("[yellow]Reset cancelled.[/yellow]")

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.Path.home")
    @patch("tgit.interactive_settings.print")
    def test_reset_settings_global_file_not_exists(self, mock_print, mock_home, mock_confirm, mock_select):
        """Test _reset_settings for global settings when file doesn't exist."""
        mock_select.return_value.ask.return_value = "global"
        mock_confirm.return_value.ask.return_value = True
        mock_home.return_value = Path("/home/user")

        with patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.unlink") as mock_unlink:
            _reset_settings()

            mock_confirm.assert_called_once()
            mock_unlink.assert_not_called()
            mock_print.assert_any_call("[yellow]Global settings file does not exist.[/yellow]")

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.print")
    def test_reset_settings_workspace_file_not_exists(self, mock_print, mock_confirm, mock_select):
        """Test _reset_settings for workspace settings when file doesn't exist."""
        mock_select.return_value.ask.return_value = "workspace"
        mock_confirm.return_value.ask.return_value = True

        with patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.unlink") as mock_unlink:
            _reset_settings()

            mock_confirm.assert_called_once()
            mock_unlink.assert_not_called()
            mock_print.assert_any_call("[yellow]Workspace settings file does not exist.[/yellow]")

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.Path.home")
    @patch("tgit.interactive_settings.print")
    def test_reset_settings_both(self, mock_print, mock_home, mock_confirm, mock_select):
        """Test _reset_settings for both global and workspace settings."""
        mock_select.return_value.ask.return_value = "both"
        mock_confirm.return_value.ask.return_value = True
        mock_home.return_value = Path("/home/user")

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.unlink") as mock_unlink,
        ):
            _reset_settings()

            mock_confirm.assert_called_once()
            assert mock_unlink.call_count == 2
            mock_print.assert_any_call("[green]Global settings reset successfully![/green]")
            mock_print.assert_any_call("[green]Workspace settings reset successfully![/green]")


class TestConfigureCommitTypes:
    """Test _configure_commit_types function."""

    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.print")
    def test_configure_commit_types_use_defaults(self, mock_print, mock_confirm):
        """Test _configure_commit_types using default types."""
        mock_confirm.return_value.ask.return_value = True

        result = _configure_commit_types([])

        assert len(result) == 10
        assert result[0] == {"type": "feat", "emoji": "✨"}
        assert result[1] == {"type": "fix", "emoji": "🐛"}
        mock_confirm.assert_called_once()

    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.print")
    def test_configure_commit_types_custom_single_type(self, mock_print, mock_text, mock_confirm):
        """Test _configure_commit_types with single custom type."""
        mock_confirm.return_value.ask.side_effect = [False, False]  # Don't use defaults, don't continue
        mock_text.return_value.ask.side_effect = ["custom", "🎯"]

        result = _configure_commit_types([])

        assert len(result) == 1
        assert result[0] == {"type": "custom", "emoji": "🎯"}

    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.print")
    def test_configure_commit_types_custom_multiple_types(self, mock_print, mock_text, mock_confirm):
        """Test _configure_commit_types with multiple custom types."""
        mock_confirm.return_value.ask.side_effect = [False, True, False]  # Don't use defaults, continue once, then stop
        mock_text.return_value.ask.side_effect = ["custom1", "🎯", "custom2", "🎨"]

        result = _configure_commit_types([])

        assert len(result) == 2
        assert result[0] == {"type": "custom1", "emoji": "🎯"}
        assert result[1] == {"type": "custom2", "emoji": "🎨"}

    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.print")
    def test_configure_commit_types_cancel_at_commit_type(self, mock_print, mock_text, mock_confirm):
        """Test _configure_commit_types with cancel at commit type."""
        mock_confirm.return_value.ask.return_value = False  # Don't use defaults
        mock_text.return_value.ask.return_value = None  # Cancel at commit type

        result = _configure_commit_types([])

        assert result == []

    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.print")
    def test_configure_commit_types_cancel_at_emoji(self, mock_print, mock_text, mock_confirm):
        """Test _configure_commit_types with cancel at emoji."""
        mock_confirm.return_value.ask.return_value = False  # Don't use defaults
        mock_text.return_value.ask.side_effect = ["custom", None]  # Enter type, cancel at emoji

        result = _configure_commit_types([])

        assert result == []

    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.print")
    def test_configure_commit_types_empty_commit_type(self, mock_print, mock_text, mock_confirm):
        """Test _configure_commit_types with empty commit type."""
        mock_confirm.return_value.ask.return_value = False  # Don't use defaults
        mock_text.return_value.ask.return_value = ""  # Empty commit type

        result = _configure_commit_types([])

        assert result == []
