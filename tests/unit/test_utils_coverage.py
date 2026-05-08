import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from tgit.cli import app
from tgit.utils import (
    _merge_settings,
    load_global_settings,
    load_workspace_settings,
    set_global_settings,
)


class TestUtilsCoverage:
    """Additional tests to increase coverage for utils and cli."""

    def test_merge_settings_nested_dict(self):
        """Test _merge_settings with nested dict values."""
        base = {"commit": {"emoji": False, "types": []}, "apiKey": "base-key"}
        override = {"commit": {"emoji": True}}
        result = _merge_settings(base, override)
        assert result["commit"]["emoji"] is True
        assert result["commit"]["types"] == []  # preserved from base
        assert result["apiKey"] == "base-key"  # preserved from base

    def test_merge_settings_flat_override(self):
        """Test _merge_settings with flat key override."""
        base = {"apiKey": "old", "model": "gpt-4"}
        override = {"apiKey": "new"}
        result = _merge_settings(base, override)
        assert result["apiKey"] == "new"
        assert result["model"] == "gpt-4"

    def test_merge_settings_scalar_overrides_dict(self):
        """Test _merge_settings when override replaces a dict with a scalar."""
        base = {"commit": {"emoji": False}}
        override = {"commit": "not-a-dict"}
        result = _merge_settings(base, override)
        assert result["commit"] == "not-a-dict"

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

    def test_cli_app_basic(self):
        """Test cli app runs without errors."""
        runner = CliRunner()
        result = runner.invoke(app, ["settings", "--help"])
        assert result.exit_code == 0

    def test_version_callback(self):
        """Test version callback."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "TGIT - ver." in result.output
