import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from tgit.add import add


class TestAdd:
    """Test cases for the add module"""

    @patch("tgit.add.simple_run_command")
    def test_add_single_file(self, mock_simple_run_command):
        """Test adding a single file"""
        runner = CliRunner()
        result = runner.invoke(add, ["test.txt"])

        assert result.exit_code == 0
        mock_simple_run_command.assert_called_once_with("git add test.txt")

    @patch("tgit.add.simple_run_command")
    def test_add_multiple_files(self, mock_simple_run_command):
        """Test adding multiple files"""
        runner = CliRunner()
        result = runner.invoke(add, ["file1.txt", "file2.py", "file3.md"])

        assert result.exit_code == 0
        mock_simple_run_command.assert_called_once_with("git add file1.txt file2.py file3.md")

    @patch("tgit.add.simple_run_command")
    def test_add_files_with_spaces(self, mock_simple_run_command):
        """Test adding files with spaces in names"""
        runner = CliRunner()
        result = runner.invoke(add, ["file with spaces.txt", "another file.py"])

        assert result.exit_code == 0
        mock_simple_run_command.assert_called_once_with("git add file with spaces.txt another file.py")

    @patch("tgit.add.simple_run_command")
    def test_add_empty_list(self, mock_simple_run_command):
        """Test adding empty file list"""
        runner = CliRunner()
        result = runner.invoke(add, [])

        # Since files argument is required=True, this should fail
        assert result.exit_code == 2
        mock_simple_run_command.assert_not_called()

    @patch("tgit.add.simple_run_command")
    def test_add_files_with_special_characters(self, mock_simple_run_command):
        """Test adding files with special characters"""
        runner = CliRunner()
        result = runner.invoke(add, ["file-with-dashes.txt", "file_with_underscores.py", "file.with.dots.md"])

        assert result.exit_code == 0
        mock_simple_run_command.assert_called_once_with("git add file-with-dashes.txt file_with_underscores.py file.with.dots.md")

    @patch("tgit.add.simple_run_command")
    def test_add_propagates_exception(self, mock_simple_run_command):
        """Test that exceptions from simple_run_command are propagated"""
        mock_simple_run_command.side_effect = Exception("Git command failed")
        runner = CliRunner()

        result = runner.invoke(add, ["test.txt"])

        # Exception should cause non-zero exit code
        assert result.exit_code != 0
