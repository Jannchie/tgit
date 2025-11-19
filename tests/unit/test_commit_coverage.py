from unittest.mock import Mock, patch

import pytest
from tgit.commit import (
    CommitArgs,
    _supports_reasoning,
    get_ai_command,
    get_file_change_sizes,
    handle_commit,
)


class TestCommitCoverage:
    """Additional tests to increase coverage for commit.py."""

    def test_supports_reasoning_empty(self):
        """Test _supports_reasoning with empty model."""
        assert _supports_reasoning("") is False
        assert _supports_reasoning(None) is False

    def test_get_file_change_sizes_value_error(self):
        """Test get_file_change_sizes with invalid numstat."""
        repo = Mock()
        # Simulate a case where numstat returns invalid integer
        repo.git.diff.return_value = "invalid\tinvalid\timage.png"
        
        sizes = get_file_change_sizes(repo)
        assert sizes["image.png"] == 0

    @patch("tgit.commit.git.Repo")
    @patch("tgit.commit.get_filtered_diff_files")
    def test_get_ai_command_no_diff(self, mock_filter, mock_repo):
        """Test get_ai_command when there is no diff after filtering."""
        repo = Mock()
        mock_repo.return_value = repo
        
        # Return some files to pass the first check
        mock_filter.return_value = (["file.txt"], [])
        
        # But make git diff return empty string
        repo.git.diff.return_value = ""
        repo.active_branch.name = "main"
        
        assert get_ai_command() is None

    @patch("tgit.commit.git.Repo")
    @patch("tgit.commit.get_filtered_diff_files")
    @patch("tgit.commit._generate_commit_with_ai")
    def test_get_ai_command_ai_failure(self, mock_gen, mock_filter, mock_repo):
        """Test get_ai_command when AI generation fails."""
        repo = Mock()
        mock_repo.return_value = repo
        mock_filter.return_value = (["file.txt"], [])
        repo.git.diff.return_value = "diff content"
        repo.active_branch.name = "main"
        
        mock_gen.return_value = None
        
        assert get_ai_command() is None

    @patch("tgit.commit.get_ai_command")
    def test_handle_commit_ai_command_none(self, mock_get_ai):
        """Test handle_commit when get_ai_command returns None."""
        mock_get_ai.return_value = None
        
        args = CommitArgs(
            message=["feat"],
            emoji=False,
            breaking=False,
            ai=False,
        )
        
        handle_commit(args)
        # Should return without error and without running command
