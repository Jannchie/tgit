"""Tests for settings_command module."""

from unittest.mock import patch

from tgit.settings_command import settings


class TestSettingsCommand:
    """Test settings command."""

    @patch("tgit.settings_command.interactive_settings")
    def test_settings_function(self, mock_interactive_settings):
        """Test that settings function calls interactive_settings."""
        settings()
        
        mock_interactive_settings.assert_called_once()

    @patch("tgit.settings_command.interactive_settings")
    def test_settings_function_passes_through(self, mock_interactive_settings):
        """Test that settings function is a simple passthrough."""
        # Call the function
        settings()
        
        # Verify it was called exactly once with no arguments
        mock_interactive_settings.assert_called_once_with()
        
        # Verify no additional side effects
        assert mock_interactive_settings.call_count == 1
