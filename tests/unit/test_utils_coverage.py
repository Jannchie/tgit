import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from tgit.cli import app
from tgit.utils import (
    load_global_settings,
    load_workspace_settings,
    set_global_settings,
)


class TestUtilsCoverage:
    """Additional tests to increase coverage for utils and cli."""

    def test_load_global_settings_empty_json(self, tmp_path):
        """Test load_global_settings with empty JSON (returns None)."""
        settings_path = tmp_path / ".tgit" / "settings.json"
        settings_path.parent.mkdir(parents=True)
        settings_path.write_text("null")
        
        with patch("tgit.utils.Path.home", return_value=tmp_path):
            settings = load_global_settings()
            assert settings == {}

    def test_load_workspace_settings_empty_json(self, tmp_path):
        """Test load_workspace_settings with empty JSON (returns None)."""
        settings_path = tmp_path / ".tgit" / "settings.json"
        settings_path.parent.mkdir(parents=True)
        settings_path.write_text("null")
        
        with patch("tgit.utils.Path.cwd", return_value=tmp_path):
            settings = load_workspace_settings()
            assert settings == {}

    def test_set_global_settings(self, tmp_path):
        """Test set_global_settings."""
        with patch("tgit.utils.Path.home", return_value=tmp_path):
            set_global_settings("test_key", "test_value")
            
            settings_path = tmp_path / ".tgit" / "settings.json"
            assert settings_path.exists()
            content = json.loads(settings_path.read_text())
            assert content["test_key"] == "test_value"
            
            # Test updating existing settings
            set_global_settings("test_key_2", "test_value_2")
            content = json.loads(settings_path.read_text())
            assert content["test_key"] == "test_value"
            assert content["test_key_2"] == "test_value_2"

    def test_set_global_settings_with_null_file(self, tmp_path):
        """Test set_global_settings when file exists but is null."""
        settings_path = tmp_path / ".tgit" / "settings.json"
        settings_path.parent.mkdir(parents=True)
        settings_path.write_text("null")
        
        with patch("tgit.utils.Path.home", return_value=tmp_path):
            set_global_settings("test_key", "test_value")
            
            content = json.loads(settings_path.read_text())
            assert content["test_key"] == "test_value"

    def test_load_global_settings_missing_file(self, tmp_path):
        """Test load_global_settings when file is missing."""
        with patch("tgit.utils.Path.home", return_value=tmp_path):
            settings = load_global_settings()
            assert settings == {}

    def test_load_workspace_settings_missing_file(self, tmp_path):
        """Test load_workspace_settings when file is missing."""
        with patch("tgit.utils.Path.cwd", return_value=tmp_path):
            settings = load_workspace_settings()
            assert settings == {}

    @patch("tgit.cli.threading.Thread")
    def test_cli_app_import_openai(self, mock_thread):
        """Test cli app triggers openai import."""
        # Mock Thread to run target immediately
        def run_target(target=None, **kwargs):
            target()
            return Mock()
            
        mock_thread.side_effect = run_target
        
        runner = CliRunner()
        # Invoke with a subcommand to ensure group function runs
        # We use a non-existent command to trigger group execution before error?
        # Or use 'version' command if available.
        # Let's use 'settings' command which is added.
        result = runner.invoke(app, ["settings", "--help"])
        
        assert result.exit_code == 0
        mock_thread.assert_called()

    @patch("tgit.cli.threading.Thread")
    def test_cli_app_import_openai_exception(self, mock_thread):
        """Test cli app handles openai import exception."""
        def run_target(target=None, **kwargs):
            # Mock import to raise exception
            with patch("builtins.__import__", side_effect=ImportError("fail")):
                target()
            return Mock()
            
        mock_thread.side_effect = run_target
        
        runner = CliRunner()
        result = runner.invoke(app, ["settings", "--help"])
        
        assert result.exit_code == 0
        mock_thread.assert_called()

    def test_version_callback(self):
        """Test version callback."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "TGIT - ver." in result.output
