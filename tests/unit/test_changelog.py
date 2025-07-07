"""Tests for changelog module."""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
from datetime import datetime, UTC
import git
import re
from click.testing import CliRunner


from tgit.changelog import (
    VersionSegment,
    Heading,
    Author,
    TGITCommit,
    ChangelogArgs,
    get_latest_git_tag,
    get_tag_by_idx,
    get_first_commit_hash,
    get_commit_hash_from_tag,
    get_simple_hash,
    ref_to_hash,
    resolve_from_ref,
    format_names,
    get_remote_uri,
    get_commits,
    group_commits_by_type,
    generate_changelog,
    extract_latest_tag_from_changelog,
    prepare_changelog_segments,
    write_changelog_prepend,
    print_and_write_changelog,
    handle_changelog,
    get_changelog_by_range,
    get_git_commits_range,
    _get_range_segments,
    _generate_changelogs_from_segments,
    _process_commits,
    _get_remote_uri_safe,
    commit_pattern,
    changelog,
)


class TestVersionSegment:
    """Test VersionSegment dataclass."""

    def test_version_segment_creation(self):
        """Test creating VersionSegment instance."""
        segment = VersionSegment(from_hash="abc123", to_hash="def456", from_name="v1.0.0", to_name="v1.1.0")
        assert segment.from_hash == "abc123"
        assert segment.to_hash == "def456"
        assert segment.from_name == "v1.0.0"
        assert segment.to_name == "v1.1.0"


class TestHeading:
    """Test Heading class."""

    def test_heading_creation(self):
        """Test creating Heading instance."""
        heading = Heading("h1")
        assert heading.tag == "h1"
        assert heading.style_name == "markdown.h1"

    def test_heading_create_classmethod(self):
        """Test Heading.create classmethod."""
        mock_token = Mock()
        mock_token.tag = "h2"
        mock_markdown = Mock()

        heading = Heading.create(mock_markdown, mock_token)
        assert heading.tag == "h2"
        assert heading.style_name == "markdown.h2"

    def test_heading_on_enter(self):
        """Test Heading.on_enter method."""
        heading = Heading("h1")
        mock_context = Mock()

        heading.on_enter(mock_context)

        assert hasattr(heading, "text")
        mock_context.enter_style.assert_called_once_with("markdown.h1")


class TestAuthor:
    """Test Author dataclass."""

    def test_author_creation(self):
        """Test creating Author instance."""
        author = Author(name="John Doe", email="john@example.com")
        assert author.name == "John Doe"
        assert author.email == "john@example.com"

    def test_author_str(self):
        """Test Author string representation."""
        author = Author(name="John Doe", email="john@example.com")
        assert str(author) == "John Doe <john@example.com>"


class TestTGITCommit:
    """Test TGITCommit class."""

    def test_tgit_commit_creation(self):
        """Test creating TGITCommit instance."""
        mock_repo = Mock()
        mock_repo.git.rev_parse.return_value = "abc1234"

        mock_commit = Mock()
        mock_commit.author.name = "John Doe"
        mock_commit.author.email = "john@example.com"
        mock_commit.committed_datetime = datetime.now(UTC)
        mock_commit.message = "feat: add new feature"
        mock_commit.hexsha = "abc1234567890"

        message_dict = {"emoji": "✨", "type": "feat", "scope": "auth", "description": "add new feature", "breaking": None}

        tgit_commit = TGITCommit(mock_repo, mock_commit, message_dict)

        assert tgit_commit.type == "feat"
        assert tgit_commit.scope == "auth"
        assert tgit_commit.description == "add new feature"
        assert tgit_commit.emoji == "✨"
        assert tgit_commit.breaking is False
        assert tgit_commit.hash == "abc1234"
        assert len(tgit_commit.authors) == 1
        assert tgit_commit.authors[0].name == "John Doe"

    def test_tgit_commit_with_co_authors(self):
        """Test TGITCommit with co-authors."""
        mock_repo = Mock()
        mock_repo.git.rev_parse.return_value = "abc1234"

        mock_commit = Mock()
        mock_commit.author.name = "John Doe"
        mock_commit.author.email = "john@example.com"
        mock_commit.committed_datetime = datetime.now(UTC)
        mock_commit.message = "feat: add new feature\n\nCo-authored-by: Jane Smith <jane@example.com>"
        mock_commit.hexsha = "abc1234567890"

        message_dict = {"type": "feat", "description": "add new feature", "breaking": None}

        tgit_commit = TGITCommit(mock_repo, mock_commit, message_dict)

        assert len(tgit_commit.authors) == 2
        assert tgit_commit.authors[0].name == "John Doe"
        assert tgit_commit.authors[1].name == "Jane Smith"

    def test_tgit_commit_breaking_change(self):
        """Test TGITCommit with breaking change."""
        mock_repo = Mock()
        mock_repo.git.rev_parse.return_value = "abc1234"

        mock_commit = Mock()
        mock_commit.author.name = "John Doe"
        mock_commit.author.email = "john@example.com"
        mock_commit.committed_datetime = datetime.now(UTC)
        mock_commit.message = "feat!: add breaking change"
        mock_commit.hexsha = "abc1234567890"

        message_dict = {"type": "feat", "description": "add breaking change", "breaking": "!"}

        tgit_commit = TGITCommit(mock_repo, mock_commit, message_dict)

        assert tgit_commit.breaking is True

    def test_tgit_commit_str(self):
        """Test TGITCommit string representation."""
        mock_repo = Mock()
        mock_repo.git.rev_parse.return_value = "abc1234"

        mock_commit = Mock()
        mock_commit.author.name = "John Doe"
        mock_commit.author.email = "john@example.com"
        mock_commit.committed_datetime = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
        mock_commit.message = "feat: add new feature"
        mock_commit.hexsha = "abc1234567890"

        message_dict = {"type": "feat", "description": "add new feature", "breaking": None}

        tgit_commit = TGITCommit(mock_repo, mock_commit, message_dict)
        str_repr = str(tgit_commit)

        assert "Hash: abc1234" in str_repr
        assert "Breaking: False" in str_repr
        assert "feat: add new feature" in str_repr
        assert "2023-01-01 12:00:00" in str_repr
        assert "John Doe <john@example.com>" in str_repr


class TestChangelogArgs:
    """Test ChangelogArgs dataclass."""

    def test_changelog_args_creation(self):
        """Test creating ChangelogArgs instance."""
        args = ChangelogArgs(path=".", from_raw="v1.0.0", to_raw="v1.1.0", verbose=1, output="CHANGELOG.md")
        assert args.path == "."
        assert args.from_raw == "v1.0.0"
        assert args.to_raw == "v1.1.0"
        assert args.verbose == 1
        assert args.output == "CHANGELOG.md"


class TestGitTagFunctions:
    """Test Git tag related functions."""

    def test_get_latest_git_tag(self):
        """Test get_latest_git_tag function."""
        mock_repo = Mock()
        mock_tag1 = Mock()
        mock_tag1.name = "v1.0.0"
        mock_tag1.commit.committed_datetime = datetime(2023, 1, 1, tzinfo=UTC)
        mock_tag2 = Mock()
        mock_tag2.name = "v1.1.0"
        mock_tag2.commit.committed_datetime = datetime(2023, 2, 1, tzinfo=UTC)

        mock_repo.tags = [mock_tag1, mock_tag2]

        result = get_latest_git_tag(mock_repo)
        assert result == "v1.1.0"

    def test_get_tag_by_idx(self):
        """Test get_tag_by_idx function."""
        mock_repo = Mock()
        mock_tag1 = Mock()
        mock_tag1.name = "v1.0.0"
        mock_tag1.commit.committed_datetime = datetime(2023, 1, 1, tzinfo=UTC)
        mock_tag2 = Mock()
        mock_tag2.name = "v1.1.0"
        mock_tag2.commit.committed_datetime = datetime(2023, 2, 1, tzinfo=UTC)

        mock_repo.tags = [mock_tag1, mock_tag2]

        result = get_tag_by_idx(mock_repo, 0)
        assert result == "v1.0.0"

        result = get_tag_by_idx(mock_repo, -1)
        assert result == "v1.1.0"

    def test_get_tag_by_idx_no_tags(self):
        """Test get_tag_by_idx with no tags."""
        mock_repo = Mock()
        mock_repo.tags = []

        result = get_tag_by_idx(mock_repo, 0)
        assert result is None

    def test_get_tag_by_idx_exception(self):
        """Test get_tag_by_idx with exception."""
        mock_repo = Mock()
        mock_repo.tags = Mock(side_effect=Exception("Git error"))

        with patch("tgit.changelog.logger") as mock_logger:
            result = get_tag_by_idx(mock_repo, 0)
            assert result is None
            mock_logger.exception.assert_called_once()

    def test_get_first_commit_hash(self):
        """Test get_first_commit_hash function."""
        mock_repo = Mock()
        mock_commit1 = Mock()
        mock_commit1.hexsha = "abc123"
        mock_commit1.parents = []
        mock_commit2 = Mock()
        mock_commit2.hexsha = "def456"
        mock_commit2.parents = [mock_commit1]

        mock_repo.iter_commits.return_value = [mock_commit2, mock_commit1]

        result = get_first_commit_hash(mock_repo)
        assert result == "abc123"

    def test_get_commit_hash_from_tag(self):
        """Test get_commit_hash_from_tag function."""
        mock_repo = Mock()
        mock_tag = Mock()
        mock_tag.commit.hexsha = "abc123456"
        mock_repo.tags = {"v1.0.0": mock_tag}

        result = get_commit_hash_from_tag(mock_repo, "v1.0.0")
        assert result == "abc123456"

    def test_get_commit_hash_from_tag_not_found(self):
        """Test get_commit_hash_from_tag with tag not found."""
        mock_repo = Mock()
        mock_repo.tags = {}

        with patch("tgit.changelog.logger") as mock_logger:
            result = get_commit_hash_from_tag(mock_repo, "v1.0.0")
            assert result is None
            mock_logger.exception.assert_called_once()


class TestHashFunctions:
    """Test hash-related functions."""

    def test_get_simple_hash(self):
        """Test get_simple_hash function."""
        mock_repo = Mock()
        mock_repo.git.rev_parse.return_value = "abc1234"

        result = get_simple_hash(mock_repo, "abc1234567890")
        assert result == "abc1234"
        mock_repo.git.rev_parse.assert_called_once_with("abc1234567890", short=7)

    def test_get_simple_hash_exception(self):
        """Test get_simple_hash with exception."""
        mock_repo = Mock()
        mock_repo.git.rev_parse.side_effect = Exception("Git error")

        with patch("tgit.changelog.logger") as mock_logger:
            result = get_simple_hash(mock_repo, "invalid_hash")
            assert result is None
            mock_logger.exception.assert_called_once()

    def test_ref_to_hash(self):
        """Test ref_to_hash function."""
        mock_repo = Mock()
        mock_repo.git.rev_parse.return_value = "abc1234"

        result = ref_to_hash(mock_repo, "main")
        assert result == "abc1234"
        mock_repo.git.rev_parse.assert_called_once_with("main", short=7)

    def test_ref_to_hash_exception(self):
        """Test ref_to_hash with exception."""
        mock_repo = Mock()
        mock_repo.git.rev_parse.side_effect = Exception("Git error")

        with patch("tgit.changelog.logger") as mock_logger:
            result = ref_to_hash(mock_repo, "invalid_ref")
            assert result is None
            mock_logger.exception.assert_called_once()


class TestResolveFromRef:
    """Test resolve_from_ref function."""

    def test_resolve_from_ref_with_value(self):
        """Test resolve_from_ref with provided value."""
        mock_repo = Mock()
        result = resolve_from_ref(mock_repo, "v1.0.0")
        assert result == "v1.0.0"

    @patch("tgit.changelog.get_latest_git_tag")
    def test_resolve_from_ref_with_tag(self, mock_get_tag):
        """Test resolve_from_ref with latest tag."""
        mock_repo = Mock()
        mock_get_tag.return_value = "v1.1.0"

        result = resolve_from_ref(mock_repo, None)
        assert result == "v1.1.0"

    @patch("tgit.changelog.get_latest_git_tag")
    @patch("tgit.changelog.get_first_commit_hash")
    def test_resolve_from_ref_no_tag(self, mock_get_first, mock_get_tag):
        """Test resolve_from_ref with no tags."""
        mock_repo = Mock()
        mock_get_tag.return_value = None
        mock_get_first.return_value = "abc123"

        result = resolve_from_ref(mock_repo, None)
        assert result == "abc123"


class TestFormatNames:
    """Test format_names function."""

    def test_format_names_empty(self):
        """Test format_names with empty list."""
        result = format_names([])
        assert result == ""

    def test_format_names_single(self):
        """Test format_names with single name."""
        result = format_names(["John"])
        assert result == "By John"

    def test_format_names_two(self):
        """Test format_names with two names."""
        result = format_names(["John", "Jane"])
        assert result == "By John and Jane"

    def test_format_names_multiple(self):
        """Test format_names with multiple names."""
        result = format_names(["John", "Jane", "Bob"])
        assert result == "By John, Jane and Bob"

    def test_format_names_many(self):
        """Test format_names with many names."""
        result = format_names(["John", "Jane", "Bob", "Alice"])
        assert result == "By John, Jane, Bob and Alice"


class TestGetRemoteUri:
    """Test get_remote_uri function."""

    def test_get_remote_uri_ssh(self):
        """Test get_remote_uri with SSH URL."""
        ssh_url = "git@github.com:user/repo.git"
        result = get_remote_uri(ssh_url)
        assert result == "github.com/user/repo"

    def test_get_remote_uri_https(self):
        """Test get_remote_uri with HTTPS URL."""
        https_url = "https://github.com/user/repo.git"
        result = get_remote_uri(https_url)
        assert result == "github.com/user/repo"

    def test_get_remote_uri_invalid(self):
        """Test get_remote_uri with invalid URL."""
        invalid_url = "not-a-git-url"
        result = get_remote_uri(invalid_url)
        assert result is None

    def test_get_remote_uri_gitlab_ssh(self):
        """Test get_remote_uri with GitLab SSH URL."""
        gitlab_url = "git@gitlab.com:user/repo.git"
        result = get_remote_uri(gitlab_url)
        assert result == "gitlab.com/user/repo"

    def test_get_remote_uri_gitlab_https(self):
        """Test get_remote_uri with GitLab HTTPS URL."""
        gitlab_url = "https://gitlab.com/user/repo.git"
        result = get_remote_uri(gitlab_url)
        assert result == "gitlab.com/user/repo"


class TestCommitPattern:
    """Test commit pattern regex."""

    def test_commit_pattern_basic(self):
        """Test commit pattern with basic commit."""
        message = "feat: add new feature"
        match = commit_pattern.match(message)
        assert match is not None
        assert match.group("type") == "feat"
        assert match.group("description") == "add new feature"
        assert match.group("scope") is None
        assert match.group("breaking") is None

    def test_commit_pattern_with_scope(self):
        """Test commit pattern with scope."""
        message = "feat(auth): add login functionality"
        match = commit_pattern.match(message)
        assert match is not None
        assert match.group("type") == "feat"
        assert match.group("scope") == "auth"
        assert match.group("description") == "add login functionality"

    def test_commit_pattern_breaking(self):
        """Test commit pattern with breaking change."""
        message = "feat!: add breaking change"
        match = commit_pattern.match(message)
        assert match is not None
        assert match.group("type") == "feat"
        assert match.group("breaking") == "!"
        assert match.group("description") == "add breaking change"

    def test_commit_pattern_with_emoji(self):
        """Test commit pattern with emoji."""
        message = "✨ feat: add new feature"
        match = commit_pattern.match(message)
        assert match is not None
        assert match.group("type") == "feat"
        assert match.group("description") == "add new feature"

    def test_commit_pattern_invalid(self):
        """Test commit pattern with invalid message."""
        message = "invalid commit message"
        match = commit_pattern.match(message)
        assert match is None


class TestGetCommits:
    """Test get_commits function."""

    @patch("tgit.changelog.commit_pattern")
    def test_get_commits(self, mock_pattern):
        """Test get_commits function."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.message = "feat: add new feature"
        mock_repo.iter_commits.return_value = [mock_commit]

        mock_match = Mock()
        mock_match.groupdict.return_value = {"type": "feat", "description": "add new feature", "scope": None, "breaking": None}
        mock_pattern.match.return_value = mock_match

        with patch("tgit.changelog.TGITCommit") as mock_tgit_commit:
            mock_tgit_commit.return_value = "mock_commit"
            result = get_commits(mock_repo, "from_hash", "to_hash")

            assert result == ["mock_commit"]
            mock_repo.iter_commits.assert_called_once_with("from_hash...to_hash")

    def test_get_commits_no_match(self):
        """Test get_commits with no matching commits."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.message = "invalid commit message"
        mock_repo.iter_commits.return_value = [mock_commit]

        result = get_commits(mock_repo, "from_hash", "to_hash")
        assert result == []


class TestGroupCommitsByType:
    """Test group_commits_by_type function."""

    def test_group_commits_by_type(self):
        """Test group_commits_by_type function."""
        mock_commit1 = Mock()
        mock_commit1.type = "feat"
        mock_commit1.breaking = False

        mock_commit2 = Mock()
        mock_commit2.type = "fix"
        mock_commit2.breaking = False

        mock_commit3 = Mock()
        mock_commit3.type = "feat"
        mock_commit3.breaking = True

        commits = [mock_commit1, mock_commit2, mock_commit3]
        result = group_commits_by_type(commits)

        assert "feat" in result
        assert "fix" in result
        assert "breaking" in result
        assert len(result["feat"]) == 1
        assert len(result["fix"]) == 1
        assert len(result["breaking"]) == 1

    def test_group_commits_by_type_breaking_priority(self):
        """Test that breaking changes take priority over type."""
        mock_commit = Mock()
        mock_commit.type = "feat"
        mock_commit.breaking = True

        result = group_commits_by_type([mock_commit])

        assert "breaking" in result
        assert "feat" not in result
        assert len(result["breaking"]) == 1


class TestGenerateChangelog:
    """Test generate_changelog function."""

    def test_generate_changelog_basic(self):
        """Test generate_changelog function."""
        mock_commit = Mock()
        mock_commit.scope = "auth"
        mock_commit.description = "add login"
        mock_commit.hash = "abc1234"
        mock_commit.authors = [Mock(name="John", email="john@example.com")]

        commits_by_type = {"feat": [mock_commit]}

        result = generate_changelog(commits_by_type, "v1.0.0", "v1.1.0")

        assert "## v1.1.0" in result
        assert "v1.0.0...v1.1.0" in result
        assert "### :sparkles: Features" in result
        assert "**auth**: add login" in result
        assert "abc1234" in result

    def test_generate_changelog_with_remote_uri(self):
        """Test generate_changelog with remote URI."""
        mock_commit = Mock()
        mock_commit.scope = None
        mock_commit.description = "add feature"
        mock_commit.hash = "abc1234"
        mock_commit.authors = [Mock(name="John", email="john@example.com")]

        commits_by_type = {"feat": [mock_commit]}

        result = generate_changelog(commits_by_type, "v1.0.0", "v1.1.0", "github.com/user/repo")

        assert "[v1.0.0...v1.1.0](https://github.com/user/repo/compare/v1.0.0...v1.1.0)" in result
        assert "[abc1234](https://github.com/user/repo/commit/abc1234)" in result

    def test_generate_changelog_breaking_changes(self):
        """Test generate_changelog with breaking changes."""
        mock_commit = Mock()
        mock_commit.scope = None
        mock_commit.description = "breaking change"
        mock_commit.hash = "abc1234"
        mock_commit.authors = [Mock(name="John", email="john@example.com")]

        commits_by_type = {"breaking": [mock_commit]}

        result = generate_changelog(commits_by_type, "v1.0.0", "v1.1.0")

        assert "### :rocket: Breaking Changes" in result
        assert "breaking change" in result


class TestExtractLatestTagFromChangelog:
    """Test extract_latest_tag_from_changelog function."""

    def test_extract_latest_tag_from_changelog(self):
        """Test extract_latest_tag_from_changelog function."""
        content = "# Changelog\n\n## v1.1.0\n\n- Some changes\n\n## v1.0.0\n\n- Initial release"

        with patch("pathlib.Path.open", mock_open(read_data=content)), patch("pathlib.Path.exists", return_value=True):
            result = extract_latest_tag_from_changelog("CHANGELOG.md")
            assert result == "v1.1.0"

    def test_extract_latest_tag_from_changelog_no_file(self):
        """Test extract_latest_tag_from_changelog with no file."""
        result = extract_latest_tag_from_changelog("nonexistent.md")
        assert result is None

    def test_extract_latest_tag_from_changelog_no_tags(self):
        """Test extract_latest_tag_from_changelog with no tags."""
        content = "# Changelog\n\nNo releases yet."

        with patch("pathlib.Path.open", mock_open(read_data=content)), patch("pathlib.Path.exists", return_value=True):
            result = extract_latest_tag_from_changelog("CHANGELOG.md")
            assert result is None


class TestWriteChangelogPrepend:
    """Test write_changelog_prepend function."""

    def test_write_changelog_prepend_existing_file(self):
        """Test write_changelog_prepend with existing file."""
        old_content = "# Changelog\n\n## v1.0.0\n\n- Initial release"
        new_content = "## v1.1.0\n\n- New feature"

        with patch("pathlib.Path.open", mock_open(read_data=old_content)) as mock_file, patch("pathlib.Path.exists", return_value=True):
            write_changelog_prepend("CHANGELOG.md", new_content)

            # Check that file was opened for reading and writing
            assert mock_file.call_count == 2

    def test_write_changelog_prepend_new_file(self):
        """Test write_changelog_prepend with new file."""
        new_content = "## v1.1.0\n\n- New feature"

        with patch("pathlib.Path.open", mock_open()) as mock_file, patch("pathlib.Path.exists", return_value=False):
            write_changelog_prepend("CHANGELOG.md", new_content)

            # Check that file was opened for writing
            mock_file.assert_called_once()


class TestPrintAndWriteChangelog:
    """Test print_and_write_changelog function."""

    @patch("tgit.changelog.console")
    def test_print_and_write_changelog_no_content(self, mock_console):
        """Test print_and_write_changelog with no content."""
        with patch("tgit.changelog.print") as mock_print:
            print_and_write_changelog("")
            mock_print.assert_called_once_with("[yellow]No changes found, nothing to output.[/yellow]")

    @patch("tgit.changelog.console")
    @patch("tgit.changelog.Markdown")
    def test_print_and_write_changelog_print_only(self, mock_markdown, mock_console):
        """Test print_and_write_changelog without output file."""
        changelog = "## v1.1.0\n\n- New feature"

        with patch("tgit.changelog.print"):
            print_and_write_changelog(changelog)

            mock_markdown.assert_called_once_with("## v1.1.0\n\n- New feature", justify="left")
            mock_console.print.assert_called()

    @patch("tgit.changelog.console")
    @patch("tgit.changelog.Markdown")
    def test_print_and_write_changelog_with_file(self, mock_markdown, mock_console):
        """Test print_and_write_changelog with output file."""
        changelog = "## v1.1.0\n\n- New feature"

        with patch("tgit.changelog.print"), patch("pathlib.Path.open", mock_open()) as mock_file:
            print_and_write_changelog(changelog, "CHANGELOG.md")

            # Check that file was written
            mock_file.assert_called_once()

    @patch("tgit.changelog.console")
    @patch("tgit.changelog.Markdown")
    @patch("tgit.changelog.write_changelog_prepend")
    def test_print_and_write_changelog_prepend(self, mock_prepend, mock_markdown, mock_console):
        """Test print_and_write_changelog with prepend."""
        changelog = "## v1.1.0\n\n- New feature"

        with patch("tgit.changelog.print"):
            print_and_write_changelog(changelog, "CHANGELOG.md", prepend=True)

            mock_prepend.assert_called_once_with("CHANGELOG.md", changelog)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_git_commits_range(self):
        """Test get_git_commits_range function."""
        mock_repo = Mock()

        with patch("tgit.changelog.resolve_from_ref") as mock_resolve:
            mock_resolve.return_value = "v1.0.0"

            from_ref, to_ref = get_git_commits_range(mock_repo, "v1.0.0", "v1.1.0")

            assert from_ref == "v1.0.0"
            assert to_ref == "v1.1.0"

    def test_get_git_commits_range_defaults(self):
        """Test get_git_commits_range with defaults."""
        mock_repo = Mock()

        with patch("tgit.changelog.resolve_from_ref") as mock_resolve:
            mock_resolve.return_value = "v1.0.0"

            from_ref, to_ref = get_git_commits_range(mock_repo, None, None)

            assert from_ref == "v1.0.0"
            assert to_ref == "HEAD"

    def test_get_remote_uri_safe_success(self):
        """Test _get_remote_uri_safe function success."""
        mock_repo = Mock()
        mock_repo.remote.return_value.url = "https://github.com/user/repo.git"

        with patch("tgit.changelog.get_remote_uri") as mock_get_uri:
            mock_get_uri.return_value = "github.com/user/repo"

            result = _get_remote_uri_safe(mock_repo)
            assert result == "github.com/user/repo"

    def test_get_remote_uri_safe_failure(self):
        """Test _get_remote_uri_safe function failure."""
        mock_repo = Mock()
        mock_repo.remote.side_effect = ValueError("No remote")

        result = _get_remote_uri_safe(mock_repo)
        assert result is None

    def test_process_commits(self):
        """Test _process_commits function."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.message = "feat: add new feature"

        with patch("tgit.changelog.commit_pattern") as mock_pattern:
            mock_match = Mock()
            mock_match.groupdict.return_value = {"type": "feat", "description": "add new feature"}
            mock_pattern.match.return_value = mock_match

            with patch("tgit.changelog.TGITCommit") as mock_tgit_commit:
                mock_tgit_commit.return_value = "mock_commit"

                result = _process_commits(mock_repo, [mock_commit])
                assert result == ["mock_commit"]


class TestChangelogFunction:
    """Test the main changelog function."""

    @patch("tgit.changelog.handle_changelog")
    def test_changelog_function_defaults(self, mock_handle):
        """Test changelog function with default arguments."""
        runner = CliRunner()
        result = runner.invoke(changelog, ["."])
        
        assert result.exit_code == 0
        mock_handle.assert_called_once()
        # Get the actual args passed to handle_changelog - it should be a ChangelogArgs object
        called_args = mock_handle.call_args[0][0]
        assert hasattr(called_args, "path")
        assert hasattr(called_args, "from_raw")
        assert hasattr(called_args, "to_raw")
        assert hasattr(called_args, "verbose")
        assert hasattr(called_args, "output")

    @patch("tgit.changelog.handle_changelog")
    def test_changelog_function_with_output_flag(self, mock_handle):
        """Test changelog function with output flag."""
        runner = CliRunner()
        result = runner.invoke(changelog, [".", "--output", ""])
        
        assert result.exit_code == 0
        mock_handle.assert_called_once()
        args = mock_handle.call_args[0][0]
        assert args.output == "CHANGELOG.md"

    @patch("tgit.changelog.handle_changelog")
    def test_changelog_function_with_custom_args(self, mock_handle):
        """Test changelog function with custom arguments."""
        runner = CliRunner()
        result = runner.invoke(changelog, ["/tmp", "--from", "v1.0.0", "--to", "v1.1.0", "-vv", "--output", "custom.md"])  # noqa: S108
        
        assert result.exit_code == 0
        mock_handle.assert_called_once()
        args = mock_handle.call_args[0][0]
        assert args.path == "/tmp"  # noqa: S108
        assert args.from_raw == "v1.0.0"
        assert args.to_raw == "v1.1.0"
        assert args.verbose == 2
        assert args.output == "custom.md"


class TestHandleChangelog:
    """Test handle_changelog function."""

    @patch("tgit.changelog.git.Repo")
    @patch("tgit.changelog.prepare_changelog_segments")
    @patch("tgit.changelog._generate_changelogs_from_segments")
    @patch("tgit.changelog.print_and_write_changelog")
    def test_handle_changelog_basic(self, mock_print, mock_generate, mock_prepare, mock_repo):
        """Test handle_changelog basic functionality."""
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance

        mock_prepare.return_value = ["segment1", "segment2"]
        mock_generate.return_value = "generated changelog"

        args = ChangelogArgs(path=".", from_raw=None, to_raw=None, verbose=0, output=None)

        handle_changelog(args)

        mock_repo.assert_called_once_with(".")
        mock_prepare.assert_called_once_with(mock_repo_instance, None, None)
        mock_generate.assert_called_once_with(mock_repo_instance, ["segment1", "segment2"])
        mock_print.assert_called_once_with("generated changelog", None, prepend=False)

    @patch("tgit.changelog.git.Repo")
    @patch("tgit.changelog.extract_latest_tag_from_changelog")
    @patch("tgit.changelog.prepare_changelog_segments")
    @patch("tgit.changelog._generate_changelogs_from_segments")
    @patch("tgit.changelog.print_and_write_changelog")
    def test_handle_changelog_with_existing_file(self, mock_print, mock_generate, mock_prepare, mock_extract, mock_repo):
        """Test handle_changelog with existing changelog file."""
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance

        mock_extract.return_value = "v1.0.0"
        mock_prepare.return_value = ["segment1"]
        mock_generate.return_value = "generated changelog"

        args = ChangelogArgs(path=".", from_raw=None, to_raw=None, verbose=0, output="CHANGELOG.md")

        with patch("pathlib.Path.exists", return_value=True):
            handle_changelog(args)

            mock_extract.assert_called_once_with("CHANGELOG.md")
            mock_prepare.assert_called_once_with(mock_repo_instance, "v1.0.0", None)
            mock_print.assert_called_once_with("generated changelog", "CHANGELOG.md", prepend=True)

    @patch("tgit.changelog.git.Repo")
    @patch("tgit.changelog._get_range_segments")
    @patch("tgit.changelog._generate_changelogs_from_segments")
    @patch("tgit.changelog.print_and_write_changelog")
    def test_handle_changelog_with_range(self, mock_print, mock_generate, mock_get_range, mock_repo):
        """Test handle_changelog with specified range."""
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance

        mock_get_range.return_value = ["segment1"]
        mock_generate.return_value = "generated changelog"

        args = ChangelogArgs(path=".", from_raw="v1.0.0", to_raw="v1.1.0", verbose=0, output=None)

        handle_changelog(args)

        mock_get_range.assert_called_once_with(mock_repo_instance, "v1.0.0", "v1.1.0")
        mock_generate.assert_called_once_with(mock_repo_instance, ["segment1"])
        mock_print.assert_called_once_with("generated changelog", None, prepend=False)
