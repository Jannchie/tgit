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
        mock_global.return_value = {
            "apiKey": "global-key",
            "model": "gpt-4"
        }
        mock_workspace.return_value = {
            "apiKey": "workspace-key"
        }
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

    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.json.loads")
    @patch("tgit.interactive_settings.Path.home")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.load_global_settings")
    def test_configure_global_settings_complete(self, mock_load_global_settings, mock_text, mock_confirm, mock_home, mock_loads, mock_dumps, mock_write_text):
        """Test _configure_global_settings complete flow."""
        mock_loads.return_value = {}
        mock_home.return_value = Path("/home/user")
        
        # Mock all questionary inputs
        mock_text.return_value.ask.side_effect = [
            "test-api-key",  # API key
            "https://api.example.com",  # API URL
            "gpt-4o"  # model
        ]
        mock_confirm.return_value.ask.side_effect = [
            True,   # show_command
            False,  # skip_confirm
            True,   # commit_emoji
            False   # configure_commit_types
        ]
        
        with patch("tgit.interactive_settings.load_global_settings", return_value={}):
            _configure_global_settings()
        
        # Verify all inputs were called
        assert mock_text.call_count == 3
        assert mock_confirm.call_count == 4
        mock_write_text.assert_called_once()


class TestConfigureWorkspaceSettings:
    """Test _configure_workspace_settings function."""

    @patch("tgit.interactive_settings.load_workspace_settings")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    def test_configure_workspace_settings_cancel(self, mock_text, mock_confirm, mock_load):
        """Test _configure_workspace_settings with cancel."""
        mock_load.return_value = {}
        mock_confirm.return_value.ask.return_value = True
        mock_text.return_value.ask.return_value = None
        
        _configure_workspace_settings()
        
        mock_text.assert_called_once()


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
            patch("pathlib.Path.exists", return_value=True) as mock_exists,
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
            patch("pathlib.Path.exists", return_value=True) as mock_exists,
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
        
        with patch("pathlib.Path.exists", return_value=False) as mock_exists, \
             patch("pathlib.Path.unlink") as mock_unlink:
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
        
        with patch("pathlib.Path.exists", return_value=False) as mock_exists, \
             patch("pathlib.Path.unlink") as mock_unlink:
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
            patch("pathlib.Path.exists", return_value=True) as mock_exists,
            patch("pathlib.Path.unlink") as mock_unlink,
        ):
            _reset_settings()
            
            mock_confirm.assert_called_once()
            assert mock_unlink.call_count == 2
            mock_print.assert_any_call("[green]Global settings reset successfully![/green]")
            mock_print.assert_any_call("[green]Workspace settings reset successfully![/green]")
