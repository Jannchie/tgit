import pytest
from unittest.mock import patch, MagicMock

from tgit.add import add


class TestAdd:
    """Test cases for the add module"""

    @patch("tgit.add.simple_run_command")
    def test_add_single_file(self, mock_simple_run_command):
        """Test adding a single file"""
        files = ["test.txt"]
        add(files)
        
        mock_simple_run_command.assert_called_once_with("git add test.txt")

    @patch("tgit.add.simple_run_command")
    def test_add_multiple_files(self, mock_simple_run_command):
        """Test adding multiple files"""
        files = ["file1.txt", "file2.py", "file3.md"]
        add(files)
        
        mock_simple_run_command.assert_called_once_with("git add file1.txt file2.py file3.md")

    @patch("tgit.add.simple_run_command")
    def test_add_files_with_spaces(self, mock_simple_run_command):
        """Test adding files with spaces in names"""
        files = ["file with spaces.txt", "another file.py"]
        add(files)
        
        mock_simple_run_command.assert_called_once_with("git add file with spaces.txt another file.py")

    @patch("tgit.add.simple_run_command")
    def test_add_empty_list(self, mock_simple_run_command):
        """Test adding empty file list"""
        files = []
        add(files)
        
        mock_simple_run_command.assert_called_once_with("git add ")

    @patch("tgit.add.simple_run_command")
    def test_add_files_with_special_characters(self, mock_simple_run_command):
        """Test adding files with special characters"""
        files = ["file-with-dashes.txt", "file_with_underscores.py", "file.with.dots.md"]
        add(files)
        
        mock_simple_run_command.assert_called_once_with("git add file-with-dashes.txt file_with_underscores.py file.with.dots.md")

    @patch("tgit.add.simple_run_command")
    def test_add_propagates_exception(self, mock_simple_run_command):
        """Test that exceptions from simple_run_command are propagated"""
        mock_simple_run_command.side_effect = Exception("Git command failed")
        
        with pytest.raises(Exception, match="Git command failed"):
            add(["test.txt"])
