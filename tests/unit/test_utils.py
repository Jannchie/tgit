from unittest.mock import patch

from tgit.utils import run_command


class TestRunCommand:
    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.questionary.confirm")
    def test_run_command_user_confirms(self, mock_confirm, mock_popen):
        """Test run_command when user confirms execution."""
        # Arrange
        mock_confirm.return_value.ask.return_value = True
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b"output", b"")
        process_mock.returncode = 0

        # Act
        run_command("echo 'test'")

        # Assert
        mock_confirm.assert_called_once_with("Do you want to continue?", default=True)
        mock_popen.assert_called_once()

    @patch("tgit.utils.subprocess.Popen")
    @patch("tgit.utils.questionary.confirm")
    def test_run_command_user_cancels(self, mock_confirm, mock_popen):
        """Test run_command when user cancels execution."""
        # Arrange
        mock_confirm.return_value.ask.return_value = False

        # Act
        run_command("echo 'test'")

        # Assert
        mock_confirm.assert_called_once_with("Do you want to continue?", default=True)
        mock_popen.assert_not_called()
