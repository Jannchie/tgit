"""Tests for interactive_settings module."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from tgit.interactive_settings import (
    _configure_commit_types,
    _configure_global_settings,
    _configure_workspace_settings,
    _mask_key,
    _reset_settings,
    interactive_settings,
)


class TestInteractiveSettings:
    """Test interactive_settings function."""

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.console.print")
    def test_interactive_settings_exit(self, mock_print, mock_select):
        """Test interactive_settings with exit choice."""
        mock_select.return_value.ask.return_value = "exit"
        interactive_settings()
        mock_select.assert_called_once()

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.console.print")
    def test_interactive_settings_cancel(self, mock_print, mock_select):
        """Test interactive_settings with cancel (None) choice."""
        mock_select.return_value.ask.return_value = None
        interactive_settings()
        mock_select.assert_called_once()

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings._configure_global_settings")
    @patch("tgit.interactive_settings.console.print")
    def test_interactive_settings_global(self, mock_print, mock_global, mock_select):
        """Test interactive_settings with global config then exit."""
        mock_select.return_value.ask.side_effect = ["global", "exit"]
        interactive_settings()
        mock_global.assert_called_once()

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings._configure_workspace_settings")
    @patch("tgit.interactive_settings.console.print")
    def test_interactive_settings_workspace(self, mock_print, mock_workspace, mock_select):
        """Test interactive_settings with workspace config then exit."""
        mock_select.return_value.ask.side_effect = ["workspace", "exit"]
        interactive_settings()
        mock_workspace.assert_called_once()

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings._reset_settings")
    @patch("tgit.interactive_settings.console.print")
    def test_interactive_settings_reset(self, mock_print, mock_reset, mock_select):
        """Test interactive_settings with reset then exit."""
        mock_select.return_value.ask.side_effect = ["reset", "exit"]
        interactive_settings()
        mock_reset.assert_called_once()


class TestMaskKey:
    """Test _mask_key function."""

    def test_mask_key_empty(self):
        assert _mask_key("") == "(not set)"

    def test_mask_key_short(self):
        assert _mask_key("sk-short") == "****"

    def test_mask_key_long(self):
        assert _mask_key("sk-1234567890abcdef") == "sk-1****cdef"

    def test_mask_key_exact_eight(self):
        assert _mask_key("12345678") == "****"


class TestConfigureGlobalSettings:
    """Test _configure_global_settings function (menu-driven)."""

    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.select")
    def test_exit_without_saving(self, mock_select, mock_load):
        """Test selecting 'Exit without Saving' immediately."""
        mock_select.return_value.ask.return_value = "exit"
        _configure_global_settings()
        mock_select.assert_called_once()

    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.select")
    def test_cancel_at_menu(self, mock_select, mock_load):
        """Test pressing Ctrl+C at main menu."""
        mock_select.return_value.ask.return_value = None
        _configure_global_settings()
        mock_select.assert_called_once()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps", return_value="{}")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.select")
    def test_save_empty(self, mock_select, mock_confirm, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test saving with no changes (empty settings)."""
        mock_select.return_value.ask.return_value = "exit"
        _configure_global_settings()
        mock_write.assert_called_once()

    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.select")
    def test_edit_provider_then_cancel_sub_prompt(self, mock_select, mock_load):
        """Test selecting provider then cancelling provider sub-prompt."""
        # First menu: pick "provider", then sub-select returns None (cancel)
        # Then main menu: pick "exit"
        mock_select.return_value.ask.side_effect = ["provider", None, "exit"]
        _configure_global_settings()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    def test_edit_provider_and_save(self, mock_select, mock_text, mock_confirm, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test changing provider then saving."""
        # First menu: pick "provider", second menu: pick "exit"
        mock_select.return_value.ask.side_effect = [
            "provider",  # pick provider in menu
            "exit",  # then save
        ]
        # Provider sub-select picks "deepseek"
        # (first select call reuses mock_select; we need to override for the sub-select)
        # Actually, the sub-select is also questionary.select, same mock.
        # First select = main menu "provider", second select = provider sub-menu "deepseek", third select = main menu "exit"
        mock_select.return_value.ask.side_effect = [
            "provider",  # main menu
            "deepseek",  # provider sub-select
            "exit",  # main menu
        ]
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert saved["provider"] == "deepseek"

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    def test_edit_model_and_save(self, mock_select, mock_text, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test changing model then saving."""
        mock_select.return_value.ask.side_effect = ["model", "exit"]
        mock_text.return_value.ask.return_value = "claude-3-opus"
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert saved["model"] == "claude-3-opus"

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.select")
    def test_toggle_boolean(self, mock_select, mock_confirm, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test toggling a boolean setting."""
        mock_select.return_value.ask.side_effect = ["show_command", "exit"]
        mock_confirm.return_value.ask.return_value = False
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert saved["show_command"] is False

    @patch("tgit.interactive_settings.load_global_settings", return_value={"apiKey": "sk-existing-key"})
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    def test_api_key_masked_display(self, mock_select, mock_text, mock_load):
        """Test API key is masked and leaving empty keeps existing."""
        mock_select.return_value.ask.side_effect = ["apiKey", "exit"]
        mock_text.return_value.ask.return_value = ""  # leave empty
        _configure_global_settings()
        # existing key should be preserved
        called_label = mock_text.call_args[0][0]
        assert "****" in called_label  # masked
        assert "keep" in called_label.lower()


class TestConfigureWorkspaceSettings:
    """Test _configure_workspace_settings function (menu-driven)."""

    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_decline_setup(self, mock_confirm, *_):
        """Test declining workspace setup."""
        mock_confirm.return_value.ask.return_value = False
        _configure_workspace_settings()
        mock_confirm.assert_called_once()

    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_exit_without_saving(self, mock_confirm, mock_select, *_):
        """Test exit from workspace menu."""
        mock_confirm.return_value.ask.return_value = True
        mock_select.return_value.ask.return_value = "exit"
        _configure_workspace_settings()
        mock_select.assert_called_once()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_save_empty(self, mock_confirm, mock_select, *_):
        """Test saving workspace with no changes."""
        mock_confirm.return_value.ask.return_value = True
        mock_select.return_value.ask.return_value = "exit"
        _configure_workspace_settings()

    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_cancel_at_menu(self, mock_confirm, mock_select, *_):
        """Test Ctrl+C at workspace menu."""
        mock_confirm.return_value.ask.return_value = True
        mock_select.return_value.ask.return_value = None
        _configure_workspace_settings()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_edit_provider_override(self, mock_confirm, mock_select, *_):
        """Test workspace provider override."""
        mock_confirm.return_value.ask.return_value = True
        mock_select.return_value.ask.side_effect = ["provider", "openai", "exit"]
        _configure_workspace_settings()


class TestResetSettings:
    """Test _reset_settings function."""

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.print")
    def test_reset_settings_cancel(self, mock_print, mock_select):
        mock_select.return_value.ask.return_value = None
        _reset_settings()
        mock_print.assert_not_called()

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.console.print")
    def test_reset_global_confirmed(self, mock_print, *_):
        """Test resetting global settings with confirmation."""
        from unittest.mock import patch as _patch
        with _patch("tgit.interactive_settings.questionary.select") as mock_s, \
             _patch("tgit.interactive_settings.questionary.confirm") as mock_c, \
             _patch("pathlib.Path.exists", return_value=True), \
             _patch("pathlib.Path.unlink") as mock_unlink, \
             _patch("tgit.interactive_settings.console.print") as mock_p:
            mock_s.return_value.ask.return_value = "global"
            mock_c.return_value.ask.return_value = True
            _reset_settings()
            mock_unlink.assert_called_once()

    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.console.print")
    def test_reset_cancelled(self, mock_print, mock_confirm, mock_select):
        """Test reset cancelled by user."""
        mock_select.return_value.ask.return_value = "global"
        mock_confirm.return_value.ask.return_value = False
        with patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.unlink") as mock_unlink:
            _reset_settings()
            mock_unlink.assert_not_called()
            mock_print.assert_any_call("Reset cancelled.")


class TestConfigureCommitTypes:
    """Test _configure_commit_types function (unchanged)."""

    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.console.print")
    def test_configure_commit_types_use_defaults(self, mock_print, mock_confirm):
        mock_confirm.return_value.ask.return_value = True
        result = _configure_commit_types([])
        assert len(result) == 10

    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.console.print")
    def test_configure_commit_types_custom_single_type(self, mock_print, mock_text, mock_confirm):
        mock_confirm.return_value.ask.side_effect = [False, False]
        mock_text.return_value.ask.side_effect = ["custom", "🎯"]
        result = _configure_commit_types([])
        assert len(result) == 1

    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.console.print")
    def test_configure_commit_types_cancel(self, mock_print, mock_text, mock_confirm):
        mock_confirm.return_value.ask.return_value = False
        mock_text.return_value.ask.return_value = None
        result = _configure_commit_types([])
        assert result == []


class TestInteractiveSettingsHelpers:
    """Tests for helper functions."""

    def test_normalize_reasoning_effort_empty(self):
        from tgit.interactive_settings import _normalize_reasoning_effort
        assert _normalize_reasoning_effort("") == ""
        assert _normalize_reasoning_effort("auto") == ""
        assert _normalize_reasoning_effort("  AUTO  ") == ""

    def test_normalize_reasoning_effort_valid(self):
        from tgit.interactive_settings import _normalize_reasoning_effort
        assert _normalize_reasoning_effort("low") == "low"
        assert _normalize_reasoning_effort("  HIGH  ") == "high"

    def test_validate_reasoning_effort_valid(self):
        from tgit.interactive_settings import _validate_reasoning_effort
        assert _validate_reasoning_effort("low") is True
        assert _validate_reasoning_effort("") is True

    def test_validate_reasoning_effort_invalid(self):
        from tgit.interactive_settings import _validate_reasoning_effort
        result = _validate_reasoning_effort("invalid")
        assert isinstance(result, str)
        assert "Use empty/auto/default" in result

    def test_supports_reasoning_model_true(self):
        from tgit.interactive_settings import _supports_reasoning_model
        assert _supports_reasoning_model("gpt-5") is True
        assert _supports_reasoning_model("o1-mini") is True

    def test_supports_reasoning_model_false(self):
        from tgit.interactive_settings import _supports_reasoning_model
        assert _supports_reasoning_model("gpt-4o") is False
        assert _supports_reasoning_model("") is False

    def test_get_default_reasoning_effort_gpt5_4(self):
        from tgit.interactive_settings import _get_default_reasoning_effort
        assert _get_default_reasoning_effort("gpt-5.4-mini") == "none"

    def test_get_default_reasoning_effort_gpt5_4_pro(self):
        from tgit.interactive_settings import _get_default_reasoning_effort
        assert _get_default_reasoning_effort("gpt-5.4-pro") == "medium"

    def test_get_default_reasoning_effort_gpt5_1(self):
        from tgit.interactive_settings import _get_default_reasoning_effort
        assert _get_default_reasoning_effort("gpt-5.1") == "none"

    def test_get_default_reasoning_effort_gpt5(self):
        from tgit.interactive_settings import _get_default_reasoning_effort
        assert _get_default_reasoning_effort("gpt-5") == "medium"

    def test_get_default_reasoning_effort_unknown(self):
        from tgit.interactive_settings import _get_default_reasoning_effort
        assert _get_default_reasoning_effort("gpt-4o") == ""

    def test_resolve_reasoning_effort_for_display_configured(self):
        from tgit.interactive_settings import _resolve_reasoning_effort_for_display
        assert _resolve_reasoning_effort_for_display("any", "high") == "high"

    def test_resolve_reasoning_effort_for_display_non_reasoning(self):
        from tgit.interactive_settings import _resolve_reasoning_effort_for_display
        assert _resolve_reasoning_effort_for_display("gpt-4o", "") == ""

    def test_resolve_reasoning_effort_for_display_reasoning(self):
        from tgit.interactive_settings import _resolve_reasoning_effort_for_display
        assert _resolve_reasoning_effort_for_display("gpt-5", "") == "medium"


class TestGlobalSettingsMoreCoverage:
    """Additional tests for _configure_global_settings coverage."""

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.select")
    def test_toggle_skip_confirm(self, mock_select, mock_confirm, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test toggling skip_confirm."""
        mock_select.return_value.ask.side_effect = ["skip_confirm", "exit"]
        mock_confirm.return_value.ask.return_value = True
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert saved["skip_confirm"] is True

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.select")
    def test_toggle_commit_emoji(self, mock_select, mock_confirm, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test toggling commit_emoji."""
        mock_select.return_value.ask.side_effect = ["commit_emoji", "exit"]
        mock_confirm.return_value.ask.return_value = True
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert saved["commit"]["emoji"] is True

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    def test_edit_api_url_and_save(self, mock_select, mock_text, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test changing API URL."""
        mock_select.return_value.ask.side_effect = ["apiUrl", "exit"]
        mock_text.return_value.ask.return_value = "https://custom.api.com"
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert saved["apiUrl"] == "https://custom.api.com"

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    def test_clear_api_url(self, mock_select, mock_text, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test clearing API URL."""
        mock_select.return_value.ask.side_effect = ["apiUrl", "exit"]
        mock_text.return_value.ask.return_value = ""
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert "apiUrl" not in saved

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    def test_set_reasoning_effort(self, mock_select, mock_text, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test setting reasoning effort."""
        mock_select.return_value.ask.side_effect = ["reasoning_effort", "exit"]
        mock_text.return_value.ask.return_value = "medium"
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert saved["reasoning_effort"] == "medium"

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    def test_clear_reasoning_effort(self, mock_select, mock_text, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test clearing reasoning effort."""
        mock_select.return_value.ask.side_effect = ["reasoning_effort", "exit"]
        mock_text.return_value.ask.return_value = "auto"
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert "reasoning_effort" not in saved

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.select")
    def test_edit_commit_types_default(self, mock_select, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test editing commit types (accepts defaults)."""
        with patch("tgit.interactive_settings.questionary.confirm") as mock_confirm:
            mock_select.return_value.ask.side_effect = ["commit_types", "exit"]
            mock_confirm.return_value.ask.return_value = True  # use defaults
            _configure_global_settings()

    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.confirm")
    @patch("tgit.interactive_settings.questionary.select")
    def test_cancel_at_boolean_sub_prompt(self, mock_select, mock_confirm, mock_load):
        """Test cancelling at boolean sub-prompt then exiting."""
        mock_select.return_value.ask.side_effect = ["show_command", "exit"]
        mock_confirm.return_value.ask.return_value = None
        _configure_global_settings()

    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    def test_cancel_at_text_sub_prompt(self, mock_select, mock_text, mock_load):
        """Test cancelling at text sub-prompt then exiting."""
        mock_select.return_value.ask.side_effect = ["model", "exit"]
        mock_text.return_value.ask.return_value = None
        _configure_global_settings()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    def test_edit_api_key_new_value(self, mock_select, mock_text, mock_load, mock_dumps, mock_write, mock_mkdir):
        """Test setting new API key value."""
        mock_select.return_value.ask.side_effect = ["apiKey", "exit"]
        mock_text.return_value.ask.return_value = "sk-new-key"
        _configure_global_settings()
        saved = mock_dumps.call_args[0][0]
        assert saved["apiKey"] == "sk-new-key"


class TestWorkspaceSettingsMoreCoverage:
    """Additional tests for _configure_workspace_settings coverage."""

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_save_empty(self, mock_confirm, mock_select, *_):
        mock_confirm.return_value.ask.return_value = True
        mock_select.return_value.ask.return_value = "exit"
        _configure_workspace_settings()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    @patch("tgit.interactive_settings.json.dumps")
    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_override_model(self, mock_confirm, mock_select, mock_text, *_):
        mock_confirm.return_value.ask.return_value = True
        mock_select.return_value.ask.side_effect = ["model", "exit"]
        mock_text.return_value.ask.return_value = "gpt-4-turbo"
        _configure_workspace_settings()

    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_cancel_at_bool_sub_prompt(self, mock_confirm, mock_select, *_):
        mock_confirm.return_value.ask.return_value = True
        # Provider menu → select show_command → _prompt_workspace_bool_setting returns WORKSPACE_PROMPT_CANCEL
        # then exit
        mock_select.return_value.ask.side_effect = ["show_command", "exit"]
        # The show_command sub-prompt has 3 choices, returning None = cancel
        # We need to mock 2 selects: first is main menu (returns show_command),
        # second is bool sub-select (returns None → WORKSPACE_PROMPT_CANCEL),
        # third is main menu (returns exit)
        mock_select.return_value.ask.side_effect = ["show_command", None, "exit"]
        _configure_workspace_settings()

    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.text")
    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_cancel_at_text_sub_prompt(self, mock_confirm, mock_select, mock_text, *_):
        mock_confirm.return_value.ask.return_value = True
        mock_select.return_value.ask.side_effect = ["model", "exit"]
        mock_text.return_value.ask.return_value = None
        _configure_workspace_settings()

    @patch("tgit.interactive_settings.load_workspace_settings", return_value={})
    @patch("tgit.interactive_settings.load_global_settings", return_value={})
    @patch("tgit.interactive_settings._get_effective_settings_dict", return_value={
        "provider": "auto", "apiKey": "", "apiUrl": "", "model": "gpt-4o-mini",
        "reasoning_effort": "", "show_command": True, "skip_confirm": False,
        "commit": {"emoji": False},
    })
    @patch("tgit.interactive_settings.questionary.select")
    @patch("tgit.interactive_settings.questionary.confirm")
    def test_cancel_at_menu(self, mock_confirm, mock_select, *_):
        mock_confirm.return_value.ask.return_value = True
        mock_select.return_value.ask.return_value = None
        _configure_workspace_settings()
