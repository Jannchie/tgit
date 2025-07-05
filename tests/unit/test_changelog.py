from datetime import UTC, datetime
from unittest.mock import Mock, patch
from tgit.changelog import get_commits, get_git_commits_range

from tgit.changelog import (
    group_commits_by_type,
)


class TestChangelog:
    """Test cases for changelog functionality."""

    def test_get_git_commits_range_with_refs(self):
        """Test getting git commits range with specific refs."""
        mock_repo = Mock()

        from_ref = "v1.0.0"
        to_ref = "v1.1.0"

        result_from, result_to = get_git_commits_range(mock_repo, from_ref, to_ref)

        assert result_from == from_ref
        assert result_to == to_ref

    def test_get_git_commits_range_empty_refs(self):
        """Test getting git commits range with empty refs."""
        mock_repo = Mock()
        mock_tag = Mock()
        mock_tag.name = "v1.0.0"
        mock_tag.commit.committed_datetime = "2024-01-01"
        mock_repo.tags = [mock_tag]

        result_from, result_to = get_git_commits_range(mock_repo, "", "")

        assert result_from == "v1.0.0"
        assert result_to == "HEAD"

    def test_get_git_commits_range_no_tags(self):
        """Test getting git commits range when no tags exist."""
        mock_repo = Mock()
        mock_repo.tags = []
        mock_repo.iter_commits.return_value = []

        result_from, result_to = get_git_commits_range(mock_repo, "", "")

        assert result_from == ""
        assert result_to == "HEAD"

    def test_get_commits(self):
        """Test getting commits from repository."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.message = "feat: add new feature"
        mock_commit.hexsha = "abc123456"
        mock_commit.author.name = "Test Author"
        mock_commit.author.email = "test@example.com"
        mock_commit.committed_datetime = datetime.fromtimestamp(1234567890, tz=UTC)

        mock_repo.iter_commits.return_value = [mock_commit]
        mock_repo.git.rev_parse.return_value = "abc1234"

        commits = get_commits(mock_repo, "v1.0.0", "HEAD")

        assert len(commits) == 1
        assert commits[0].description == "add new feature"
        assert commits[0].hash == "abc1234"
        assert commits[0].type == "feat"
        assert len(commits[0].authors) == 1
        assert commits[0].authors[0].name == "Test Author"
        assert commits[0].authors[0].email == "test@example.com"

    def test_group_commits_by_type(self):
        """Test grouping commits by type."""
        mock_commit1 = Mock()
        mock_commit1.type = "feat"
        mock_commit1.message = "feat: add feature"
        mock_commit1.breaking = False

        mock_commit2 = Mock()
        mock_commit2.type = "fix"
        mock_commit2.message = "fix: bug fix"
        mock_commit2.breaking = False

        mock_commit3 = Mock()
        mock_commit3.type = "feat"
        mock_commit3.message = "feat: another feature"
        mock_commit3.breaking = False

        commits = [mock_commit1, mock_commit2, mock_commit3]

        grouped = group_commits_by_type(commits)

        assert "feat" in grouped
        assert "fix" in grouped
        assert len(grouped["feat"]) == 2
        assert len(grouped["fix"]) == 1

    def test_group_commits_by_type_breaking(self):
        """Test grouping commits with breaking changes."""
        mock_commit = Mock()
        mock_commit.type = "feat"
        mock_commit.message = "feat!: breaking change"
        mock_commit.breaking = True

        commits = [mock_commit]

        grouped = group_commits_by_type(commits)

        assert "breaking" in grouped
        assert len(grouped["breaking"]) == 1

    def test_group_commits_by_type_empty(self):
        """Test grouping empty commits list."""
        commits = []

        grouped = group_commits_by_type(commits)

        assert grouped == {}

    @patch("tgit.changelog.get_commits")
    @patch("tgit.changelog.get_git_commits_range")
    def test_changelog_integration(self, mock_get_range, mock_get_commits):
        """Test changelog generation integration."""
        # Setup mocks
        mock_get_range.return_value = ("v1.0.0", "HEAD")

        mock_commit = Mock()
        mock_commit.type = "feat"
        mock_commit.message = "feat: new feature"
        mock_commit.hash = "abc123"
        mock_commit.author = "Test Author"
        mock_commit.email = "test@example.com"
        mock_commit.date = "2024-01-01"
        mock_commit.breaking = False

        mock_get_commits.return_value = [mock_commit]

        mock_repo = Mock()
        from_ref, to_ref = get_git_commits_range(mock_repo, "", "")
        commits = get_commits(mock_repo, from_ref, to_ref)

        assert len(commits) == 1
        assert commits[0].type == "feat"
        assert commits[0].message == "feat: new feature"
