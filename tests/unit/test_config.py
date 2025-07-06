import pytest
from unittest.mock import patch, MagicMock
import typer

from tgit.config import config


class TestConfig:
    """Test cases for the config module"""

    @patch("tgit.config.interactive_settings")
    def test_config_interactive_flag(self, mock_interactive_settings):
        """Test config with interactive flag"""
        config(key=None, value=None, interactive=True)
        
        mock_interactive_settings.assert_called_once()

    @patch("tgit.config.interactive_settings")
    def test_config_no_args_defaults_to_interactive(self, mock_interactive_settings):
        """Test config with no arguments defaults to interactive mode"""
        config(key=None, value=None, interactive=False)
        
        mock_interactive_settings.assert_called_once()

    @patch("tgit.config.print")
    def test_config_missing_key_only(self, mock_print):
        """Test config with missing key only"""
        with pytest.raises(typer.Exit) as exc_info:
            config(key=None, value="test", interactive=False)
        
        assert exc_info.value.exit_code == 1
        mock_print.assert_any_call("Both key and value are required when not using interactive mode")
        mock_print.assert_any_call("Use --interactive or -i for interactive configuration")

    @patch("tgit.config.print")
    def test_config_missing_value_only(self, mock_print):
        """Test config with missing value only"""
        with pytest.raises(typer.Exit) as exc_info:
            config(key="apiKey", value=None, interactive=False)
        
        assert exc_info.value.exit_code == 1
        mock_print.assert_any_call("Both key and value are required when not using interactive mode")
        mock_print.assert_any_call("Use --interactive or -i for interactive configuration")

    @patch("tgit.config.print")
    def test_config_invalid_key(self, mock_print):
        """Test config with invalid key"""
        with pytest.raises(typer.Exit) as exc_info:
            config(key="invalid_key", value="test", interactive=False)
        
        assert exc_info.value.exit_code == 1
        available_keys = ["apiKey", "apiUrl", "model", "show_command", "skip_confirm"]
        mock_print.assert_called_once_with(f"Key invalid_key is not valid. Available keys: {', '.join(available_keys)}")

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_config_valid_string_key(self, mock_print, mock_set_global_settings):
        """Test config with valid string key"""
        config(key="apiKey", value="test_key", interactive=False)
        
        mock_set_global_settings.assert_called_once_with("apiKey", "test_key")
        mock_print.assert_called_once_with("[green]Setting apiKey updated successfully![/green]")

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_config_valid_model_key(self, mock_print, mock_set_global_settings):
        """Test config with valid model key"""
        config(key="model", value="gpt-4", interactive=False)
        
        mock_set_global_settings.assert_called_once_with("model", "gpt-4")
        mock_print.assert_called_once_with("[green]Setting model updated successfully![/green]")

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_config_boolean_true_values(self, mock_print, mock_set_global_settings):
        """Test config with boolean true values"""
        true_values = ["true", "1", "yes", "on", "TRUE", "YES", "ON"]
        
        for value in true_values:
            mock_set_global_settings.reset_mock()
            mock_print.reset_mock()
            
            config(key="show_command", value=value, interactive=False)
            
            mock_set_global_settings.assert_called_once_with("show_command", True)
            mock_print.assert_called_once_with("[green]Setting show_command updated successfully![/green]")

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_config_boolean_false_values(self, mock_print, mock_set_global_settings):
        """Test config with boolean false values"""
        false_values = ["false", "0", "no", "off", "FALSE", "NO", "OFF"]
        
        for value in false_values:
            mock_set_global_settings.reset_mock()
            mock_print.reset_mock()
            
            config(key="skip_confirm", value=value, interactive=False)
            
            mock_set_global_settings.assert_called_once_with("skip_confirm", False)
            mock_print.assert_called_once_with("[green]Setting skip_confirm updated successfully![/green]")

    @patch("tgit.config.print")
    def test_config_invalid_boolean_value(self, mock_print):
        """Test config with invalid boolean value"""
        with pytest.raises(typer.Exit) as exc_info:
            config(key="show_command", value="invalid", interactive=False)
        
        assert exc_info.value.exit_code == 1
        mock_print.assert_called_once_with("Invalid boolean value for show_command. Use true/false, 1/0, yes/no, or on/off")

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_config_all_valid_keys(self, mock_print, mock_set_global_settings):
        """Test config with all valid keys"""
        valid_configs = [
            ("apiKey", "test_key"),
            ("apiUrl", "https://api.openai.com"),
            ("model", "gpt-4"),
            ("show_command", "true"),
            ("skip_confirm", "false"),
        ]
        
        for key, value in valid_configs:
            mock_set_global_settings.reset_mock()
            mock_print.reset_mock()
            
            config(key=key, value=value, interactive=False)
            
            # Convert expected value for boolean keys
            expected_value = value
            if key in ["show_command", "skip_confirm"]:
                expected_value = value.lower() == "true"
            
            mock_set_global_settings.assert_called_once_with(key, expected_value)
            mock_print.assert_called_once_with(f"[green]Setting {key} updated successfully![/green]")

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.interactive_settings")
    def test_config_interactive_takes_precedence(self, mock_interactive_settings, mock_set_global_settings):
        """Test that interactive flag takes precedence over provided key/value"""
        config(key="apiKey", value="test", interactive=True)
        
        mock_interactive_settings.assert_called_once()
        mock_set_global_settings.assert_not_called()
