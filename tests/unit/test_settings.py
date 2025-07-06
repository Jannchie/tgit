import pytest
from unittest.mock import patch, MagicMock
import json

from tgit.settings import (
    settings,
    _merge_settings,
    _dict_to_settings,
)
from tgit.types import TGitSettings


class TestSettings:
    def test_settings_initial_state(self):
        """Test that settings object has correct initial state."""
        assert hasattr(settings, "api_key")
        assert hasattr(settings, "api_url")
        assert hasattr(settings, "model")
        assert hasattr(settings, "show_command")
        assert hasattr(settings, "skip_confirm")
        assert hasattr(settings, "commit")

    def test_merge_settings_basic(self):
        """Test basic settings merging."""
        global_settings = {"apiKey": "global_key", "model": "gpt-3.5-turbo"}
        workspace_settings = {"apiKey": "workspace_key", "show_command": True}
        
        result = _merge_settings(global_settings, workspace_settings)
        
        expected = {
            "apiKey": "workspace_key",  # workspace overrides global
            "model": "gpt-3.5-turbo",   # from global
            "show_command": True        # from workspace
        }
        assert result == expected

    def test_merge_settings_empty_workspace(self):
        """Test settings merging with empty workspace settings."""
        global_settings = {"apiKey": "global_key", "model": "gpt-4"}
        workspace_settings = {}
        
        result = _merge_settings(global_settings, workspace_settings)
        
        assert result == global_settings

    def test_merge_settings_empty_global(self):
        """Test settings merging with empty global settings."""
        global_settings = {}
        workspace_settings = {"apiKey": "workspace_key", "show_command": True}
        
        result = _merge_settings(global_settings, workspace_settings)
        
        assert result == workspace_settings

    def test_merge_settings_both_empty(self):
        """Test settings merging with both empty."""
        global_settings = {}
        workspace_settings = {}
        
        result = _merge_settings(global_settings, workspace_settings)
        
        assert result == {}

    def test_merge_settings_nested_commit(self):
        """Test settings merging with nested commit settings."""
        global_settings = {
            "apiKey": "global_key",
            "commit": {
                "emoji": False,
                "types": [{"type": "feat", "emoji": ":sparkles:"}]
            }
        }
        workspace_settings = {
            "commit": {
                "emoji": True,
                "types": [{"type": "feat", "emoji": ":star:"}, {"type": "fix", "emoji": ":bug:"}]
            }
        }
        
        result = _merge_settings(global_settings, workspace_settings)
        
        expected = {
            "apiKey": "global_key",
            "commit": {
                "emoji": True,
                "types": [{"type": "feat", "emoji": ":star:"}, {"type": "fix", "emoji": ":bug:"}]
            }
        }
        assert result == expected

    def test_dict_to_settings_basic(self):
        """Test conversion from dict to TGitSettings."""
        data = {
            "apiKey": "test_key",
            "apiUrl": "https://api.openai.com",
            "model": "gpt-4",
            "show_command": True,
            "skip_confirm": False
        }
        
        result = _dict_to_settings(data)
        
        assert isinstance(result, TGitSettings)
        assert result.api_key == "test_key"
        assert result.api_url == "https://api.openai.com"
        assert result.model == "gpt-4"
        assert result.show_command is True
        assert result.skip_confirm is False

    def test_dict_to_settings_with_commit(self):
        """Test conversion from dict to TGitSettings with commit settings."""
        data = {
            "apiKey": "test_key",
            "commit": {
                "emoji": True,
                "types": [
                    {"type": "feat", "emoji": ":sparkles:"},
                    {"type": "fix", "emoji": ":bug:"}
                ]
            }
        }
        
        result = _dict_to_settings(data)
        
        assert isinstance(result, TGitSettings)
        assert result.commit.emoji is True
        assert len(result.commit.types) == 2
        assert result.commit.types[0].type == "feat"
        assert result.commit.types[0].emoji == ":sparkles:"
        assert result.commit.types[1].type == "fix"
        assert result.commit.types[1].emoji == ":bug:"

    def test_dict_to_settings_defaults(self):
        """Test conversion from dict to TGitSettings with defaults."""
        data = {}
        
        result = _dict_to_settings(data)
        
        assert isinstance(result, TGitSettings)
        assert result.api_key == ""
        assert result.api_url == ""
        assert result.model == ""
        assert result.show_command is True
        assert result.skip_confirm is False
        assert result.commit.emoji is False
        assert len(result.commit.types) == 0

