from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import yaml

from tgit.settings import (
    load_global_settings,
    set_global_settings,
    load_workspace_settings,
    load_settings,
    settings,
)


class TestLoadGlobalSettings:
    def test_load_global_settings_yaml_exists(self):
        """Test loading global settings when .tgit.yaml exists"""
        # Create actual Path objects to test against
        yaml_content = "apiKey: test-key\nmodel: gpt-4"

        with patch("tgit.settings.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")

            # Mock the yaml path to exist and contain content
            with patch.object(Path, "exists") as mock_exists, patch.object(Path, "read_text") as mock_read:
                # First path (.tgit.yaml) exists, second (.tgit.yml) doesn't
                mock_exists.side_effect = [True, False]
                mock_read.return_value = yaml_content

                result = load_global_settings()

                assert result == {"apiKey": "test-key", "model": "gpt-4"}

    def test_load_global_settings_yml_exists(self):
        """Test loading global settings when .tgit.yml exists"""
        yaml_content = "apiKey: test-key-yml\nmodel: gpt-3.5"

        with patch("tgit.settings.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")

            with patch.object(Path, "exists") as mock_exists, patch.object(Path, "read_text") as mock_read:
                # First path (.tgit.yaml) doesn't exist, second (.tgit.yml) does
                mock_exists.side_effect = [False, True]
                mock_read.return_value = yaml_content

                result = load_global_settings()

                assert result == {"apiKey": "test-key-yml", "model": "gpt-3.5"}

    def test_load_global_settings_no_file(self):
        """Test loading global settings when no file exists"""
        with patch("tgit.settings.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")

            with patch.object(Path, "exists", return_value=False):
                result = load_global_settings()

                assert result == {}

    def test_load_global_settings_empty_file(self):
        """Test loading global settings from empty file"""
        with patch("tgit.settings.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")

            with patch.object(Path, "exists") as mock_exists, patch.object(Path, "read_text") as mock_read:
                mock_exists.side_effect = [True, False]
                mock_read.return_value = ""

                result = load_global_settings()

                assert result == {}

    def test_load_global_settings_invalid_yaml(self):
        """Test loading global settings with invalid YAML"""
        with patch("tgit.settings.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")

            with patch.object(Path, "exists") as mock_exists, patch.object(Path, "read_text") as mock_read:
                mock_exists.side_effect = [True, False]
                mock_read.return_value = "invalid: yaml: content"

                with pytest.raises(yaml.YAMLError):
                    load_global_settings()


class TestSetGlobalSettings:
    def test_set_global_settings_existing_file(self):
        """Test setting global settings when file exists"""
        with patch("tgit.settings.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")

            with (
                patch.object(Path, "exists") as mock_exists,
                patch.object(Path, "read_text") as mock_read,
                patch.object(Path, "write_text") as mock_write,
            ):
                mock_exists.side_effect = [True, False]
                mock_read.return_value = "apiKey: old-key"

                set_global_settings("model", "gpt-4")

                mock_write.assert_called_once()
                written_content = mock_write.call_args[0][0]
                data = yaml.safe_load(written_content)
                assert data == {"apiKey": "old-key", "model": "gpt-4"}

    def test_set_global_settings_no_existing_file(self):
        """Test setting global settings when no file exists"""
        with patch("tgit.settings.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")

            with patch.object(Path, "exists", return_value=False), patch.object(Path, "write_text") as mock_write:
                set_global_settings("apiKey", "new-key")

                mock_write.assert_called_once()
                written_content = mock_write.call_args[0][0]
                data = yaml.safe_load(written_content)
                assert data == {"apiKey": "new-key"}

    def test_set_global_settings_empty_existing_file(self):
        """Test setting global settings when existing file is empty"""
        with patch("tgit.settings.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")

            with (
                patch.object(Path, "exists") as mock_exists,
                patch.object(Path, "read_text") as mock_read,
                patch.object(Path, "write_text") as mock_write,
            ):
                mock_exists.side_effect = [True, False]
                mock_read.return_value = ""

                set_global_settings("model", "gpt-4")

                mock_write.assert_called_once()
                written_content = mock_write.call_args[0][0]
                data = yaml.safe_load(written_content)
                assert data == {"model": "gpt-4"}


class TestLoadWorkspaceSettings:
    def test_load_workspace_settings_yaml_exists(self):
        """Test loading workspace settings when .tgit.yaml exists"""
        yaml_content = "commit:\n  emoji: true"

        with patch("tgit.settings.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/project")

            with patch.object(Path, "exists") as mock_exists, patch.object(Path, "read_text") as mock_read:
                mock_exists.side_effect = [True, False]
                mock_read.return_value = yaml_content

                result = load_workspace_settings()

                assert result == {"commit": {"emoji": True}}

    def test_load_workspace_settings_yml_exists(self):
        """Test loading workspace settings when .tgit.yml exists"""
        yaml_content = "commit:\n  emoji: false"

        with patch("tgit.settings.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/project")

            with patch.object(Path, "exists") as mock_exists, patch.object(Path, "read_text") as mock_read:
                mock_exists.side_effect = [False, True]
                mock_read.return_value = yaml_content

                result = load_workspace_settings()

                assert result == {"commit": {"emoji": False}}

    def test_load_workspace_settings_no_file(self):
        """Test loading workspace settings when no file exists"""
        with patch("tgit.settings.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/project")

            with patch.object(Path, "exists", return_value=False):
                result = load_workspace_settings()

                assert result == {}


class TestLoadSettings:
    @patch("tgit.settings.load_global_settings")
    @patch("tgit.settings.load_workspace_settings")
    def test_load_settings_merge(self, mock_workspace, mock_global):
        """Test loading and merging global and workspace settings"""
        mock_global.return_value = {"apiKey": "global-key", "model": "gpt-4"}
        mock_workspace.return_value = {"apiKey": "workspace-key", "commit": {"emoji": True}}

        # Clear existing settings
        settings.clear()

        result = load_settings()

        expected = {
            "apiKey": "workspace-key",  # workspace overrides global
            "model": "gpt-4",
            "commit": {"emoji": True},
        }
        assert result == expected
        assert settings == expected

    @patch("tgit.settings.load_global_settings")
    @patch("tgit.settings.load_workspace_settings")
    def test_load_settings_global_only(self, mock_workspace, mock_global):
        """Test loading settings with only global settings"""
        mock_global.return_value = {"apiKey": "global-key", "model": "gpt-4"}
        mock_workspace.return_value = {}

        # Clear existing settings
        settings.clear()

        result = load_settings()

        expected = {"apiKey": "global-key", "model": "gpt-4"}
        assert result == expected
        assert settings == expected

    @patch("tgit.settings.load_global_settings")
    @patch("tgit.settings.load_workspace_settings")
    def test_load_settings_workspace_only(self, mock_workspace, mock_global):
        """Test loading settings with only workspace settings"""
        mock_global.return_value = {}
        mock_workspace.return_value = {"commit": {"emoji": True}}

        # Clear existing settings
        settings.clear()

        result = load_settings()

        expected = {"commit": {"emoji": True}}
        assert result == expected
        assert settings == expected

    @patch("tgit.settings.load_global_settings")
    @patch("tgit.settings.load_workspace_settings")
    def test_load_settings_empty(self, mock_workspace, mock_global):
        """Test loading settings when both are empty"""
        mock_global.return_value = {}
        mock_workspace.return_value = {}

        # Clear existing settings
        settings.clear()

        result = load_settings()

        assert result == {}
        assert settings == {}

    @patch("tgit.settings.load_global_settings")
    @patch("tgit.settings.load_workspace_settings")
    def test_load_settings_nested_override(self, mock_workspace, mock_global):
        """Test loading settings with nested dictionary override"""
        mock_global.return_value = {"commit": {"emoji": False, "types": ["feat", "fix"]}, "apiKey": "global-key"}
        mock_workspace.return_value = {"commit": {"emoji": True}}

        # Clear existing settings
        settings.clear()

        result = load_settings()

        expected = {
            "commit": {"emoji": True},  # workspace completely overrides global commit settings
            "apiKey": "global-key",
        }
        assert result == expected
        assert settings == expected
