from unittest.mock import Mock, patch

import pytest
from tgit.changelog import (
    get_changelog_by_range,
    get_commits,
    prepare_changelog_segments,
)


class TestChangelogCoverage:
    """Additional tests to increase coverage for changelog.py."""

    @patch("tgit.changelog.commit_pattern")
    def test_get_commits_bytes_message(self, mock_pattern):
        """Test get_commits with bytes message."""
        repo = Mock()
        commit = Mock()
        commit.message = b"feat: bytes message"
        repo.iter_commits.return_value = [commit]
        
        mock_pattern.match.return_value = None  # Just to avoid further processing
        
        get_commits(repo, "HEAD~1", "HEAD")
        
        # Verify message was decoded
        # Since we mocked match to return None, we can't verify the result list,
        # but we can verify that no error occurred during decoding.

    @patch("tgit.changelog.commit_pattern")
    def test_get_commits_non_string_message(self, mock_pattern):
        """Test get_commits with non-string message."""
        repo = Mock()
        commit = Mock()
        commit.message = 12345
        repo.iter_commits.return_value = [commit]
        
        mock_pattern.match.return_value = None
        
        get_commits(repo, "HEAD~1", "HEAD")

    def test_prepare_changelog_segments_with_latest_tag_in_file(self):
        """Test prepare_changelog_segments with latest_tag_in_file."""
        repo = Mock()
        tag1 = Mock()
        tag1.name = "v1.0.0"
        tag1.commit.hexsha = "hash1"
        tag1.commit.committed_datetime = 1000
        
        tag2 = Mock()
        tag2.name = "v1.1.0"
        tag2.commit.hexsha = "hash2"
        tag2.commit.committed_datetime = 2000
        
        repo.tags = [tag1, tag2]
        repo.iter_commits.return_value = [Mock(hexsha="init")]
        
        # Mock get_first_commit_hash
        with patch("tgit.changelog.get_first_commit_hash", return_value="init"):
            segments = prepare_changelog_segments(repo, latest_tag_in_file="v1.0.0")
            
            assert len(segments) == 1
            assert segments[0].from_name == "v1.0.0"
            assert segments[0].to_name == "v1.1.0"

    @patch("tgit.changelog.get_commits")
    @patch("tgit.changelog.group_commits_by_type")
    @patch("tgit.changelog.generate_changelog")
    def test_get_changelog_by_range_no_remote(self, mock_gen, mock_group, mock_get_commits):
        """Test get_changelog_by_range when remote is missing."""
        repo = Mock()
        repo.remote.side_effect = ValueError("No remote")
        
        with pytest.warns(UserWarning, match="Origin not found"):
            get_changelog_by_range(repo, "HEAD~1", "HEAD")
            
        mock_gen.assert_called_once()
        assert mock_gen.call_args[0][3] is None  # remote_uri should be None
