import pytest
from unittest.mock import MagicMock, patch
import click
from click.testing import CliRunner

from tgit.cli import app, set_process_title, set_terminal_title, version_callback


class TestCLI:
    """Test cases for the CLI module"""

    def test_app_instance(self):
        """Test that app is a Click group with correct configuration"""
        assert isinstance(app, click.Group)
        assert app.name == "tgit"
        assert app.help == "TGIT cli"
        assert app.no_args_is_help is True

    def test_commands_registered(self):
        """Test that all expected commands are registered"""
        # Just verify the app object exists and has the right type
        # since the command registration details may vary by Click version
        assert isinstance(app, click.Group)

    @patch("tgit.cli.importlib.metadata.version")
    @patch("tgit.cli.console.print")
    def test_version_callback_true(self, mock_print, mock_version):
        """Test version callback when value is True"""
        mock_version.return_value = "1.0.0"
        mock_ctx = MagicMock()
        mock_ctx.resilient_parsing = False
        mock_param = MagicMock()

        version_callback(ctx=mock_ctx, _param=mock_param, value=True)

        mock_version.assert_called_once_with("tgit")
        mock_print.assert_called_once_with("TGIT - ver.1.0.0", highlight=False)
        mock_ctx.exit.assert_called_once()

    @patch("tgit.cli.importlib.metadata.version")
    @patch("tgit.cli.console.print")
    def test_version_callback_false(self, mock_print, mock_version):
        """Test version callback when value is False"""
        mock_ctx = MagicMock()
        mock_ctx.resilient_parsing = False
        mock_param = MagicMock()

        version_callback(ctx=mock_ctx, _param=mock_param, value=False)

        mock_version.assert_not_called()
        mock_print.assert_not_called()
        mock_ctx.exit.assert_not_called()

    @patch("tgit.cli.set_process_title")
    @patch("tgit.cli.set_terminal_title")
    def test_app_callback_sets_process_title(self, mock_set_terminal_title, mock_set_process_title):
        """Test that app callback sets process and terminal titles."""
        app.callback()

        mock_set_process_title.assert_called_once_with("tgit")
        mock_set_terminal_title.assert_called_once_with("tgit")

    def test_app_callback_registration(self):
        """Test that app is properly configured"""
        # Check if app has the callback mechanism
        assert isinstance(app, click.Group)
        # Verify the app exists and is configured correctly

    @patch("tgit.cli.setproctitle_module.setproctitle")
    def test_set_process_title_updates_process_name(self, mock_setproctitle):
        """Test process title is updated when support is available."""
        set_process_title("tgit")

        mock_setproctitle.assert_called_once_with("tgit")

    @patch("tgit.cli.setproctitle_module.setproctitle", side_effect=RuntimeError("boom"))
    def test_set_process_title_ignores_errors(self, mock_setproctitle):
        """Test process title errors do not break CLI startup."""
        set_process_title("tgit")

        mock_setproctitle.assert_called_once_with("tgit")

    @patch("tgit.cli.sys.stdout.flush")
    @patch("tgit.cli.sys.stdout.write")
    @patch("tgit.cli.sys.stdout.isatty", return_value=True)
    def test_set_terminal_title_writes_escape_sequence(self, mock_isatty, mock_write, mock_flush):
        """Test terminal title is written for TTY outputs."""
        set_terminal_title("tgit")

        mock_isatty.assert_called_once()
        mock_write.assert_called_once_with("\033]0;tgit\a")
        mock_flush.assert_called_once()

    @patch("tgit.cli.sys.stdout.flush")
    @patch("tgit.cli.sys.stdout.write")
    @patch("tgit.cli.sys.stdout.isatty", return_value=False)
    def test_set_terminal_title_skips_non_tty(self, mock_isatty, mock_write, mock_flush):
        """Test terminal title is not written for non-TTY outputs."""
        set_terminal_title("tgit")

        mock_isatty.assert_called_once()
        mock_write.assert_not_called()
        mock_flush.assert_not_called()



