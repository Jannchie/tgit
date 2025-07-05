import argparse
from unittest.mock import Mock, patch

import git
import pytest

from tgit.commit import (
    MAX_DIFF_LINES,
    CommitArgs,
    CommitData,
    _check_openai_availability,
    _create_openai_client,
    _import_openai,
    define_commit_parser,
    get_changed_files_from_status,
    get_file_change_sizes,
    get_filtered_diff_files,
)


class TestCommitArgs:
    def test_commit_args_creation(self):
        """Test CommitArgs dataclass creation"""
        args = CommitArgs(
            message=["feat", "scope", "add new feature"],
            emoji=True,
            breaking=False,
            ai=True,
        )
        assert args.message == ["feat", "scope", "add new feature"]
        assert args.emoji is True
        assert args.breaking is False
        assert args.ai is True


class TestCommitData:
    def test_commit_data_validation(self):
        """Test CommitData pydantic model validation"""
        data = CommitData(
            type="feat",
            scope="api",
            msg="add new endpoint",
            is_breaking=False,
        )
        assert data.type == "feat"
        assert data.scope == "api"
        assert data.msg == "add new endpoint"
        assert data.is_breaking is False

    def test_commit_data_no_scope(self):
        """Test CommitData with no scope"""
        data = CommitData(
            type="fix",
            scope=None,
            msg="fix bug",
            is_breaking=False,
        )
        assert data.type == "fix"
        assert data.scope is None
        assert data.msg == "fix bug"
        assert data.is_breaking is False


class TestDefineCommitParser:
    @patch("tgit.commit.settings")
    def test_define_commit_parser_basic(self, mock_settings):
        """Test basic commit parser definition"""
        mock_settings.get.return_value = {}

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        define_commit_parser(subparsers)

        # Parse arguments to verify parser was created correctly
        args = parser.parse_args(["commit", "feat", "add", "feature"])
        assert args.message == ["feat", "add", "feature"]
        assert args.emoji is False
        assert args.breaking is False
        assert args.ai is False

    @patch("tgit.commit.settings")
    def test_define_commit_parser_with_flags(self, mock_settings):
        """Test commit parser with flags"""
        mock_settings.get.return_value = {}

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        define_commit_parser(subparsers)

        # Parse arguments with flags
        args = parser.parse_args(["commit", "--emoji", "--breaking", "--ai", "feat", "add", "feature"])
        assert args.message == ["feat", "add", "feature"]
        assert args.emoji is True
        assert args.breaking is True
        assert args.ai is True

    @patch("tgit.commit.settings")
    def test_define_commit_parser_with_custom_types(self, mock_settings):
        """Test commit parser with custom commit types"""
        mock_settings.get.return_value = {
            "types": [
                {"type": "custom", "emoji": "🎨"},
                {"type": "another", "emoji": "🔧"},
            ],
        }

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        define_commit_parser(subparsers)

        # Should not raise an error
        args = parser.parse_args(["commit", "custom", "test"])
        assert args.message == ["custom", "test"]


class TestGetChangedFilesFromStatus:
    def test_get_changed_files_added_modified(self):
        """Test getting changed files for added/modified files"""
        mock_repo = Mock(spec=git.Repo)
        mock_repo.git.diff.return_value = "A\tfile1.py\nM\tfile2.py\nD\tfile3.py"

        result = get_changed_files_from_status(mock_repo)

        assert result == {"file1.py", "file2.py", "file3.py"}
        mock_repo.git.diff.assert_called_once_with("--cached", "--name-status", "-M")

    def test_get_changed_files_renamed(self):
        """Test getting changed files for renamed files"""
        mock_repo = Mock(spec=git.Repo)
        mock_repo.git.diff.return_value = "R100\told_file.py\tnew_file.py\nM\tother_file.py"

        result = get_changed_files_from_status(mock_repo)

        assert result == {"old_file.py", "new_file.py", "other_file.py"}

    def test_get_changed_files_empty(self):
        """Test getting changed files when no files changed"""
        mock_repo = Mock(spec=git.Repo)
        mock_repo.git.diff.return_value = ""

        result = get_changed_files_from_status(mock_repo)

        assert result == set()

    def test_get_changed_files_malformed_line(self):
        """Test handling malformed diff lines"""
        mock_repo = Mock(spec=git.Repo)
        mock_repo.git.diff.return_value = "A\tfile1.py\nmalformed_line\nM\tfile2.py"

        result = get_changed_files_from_status(mock_repo)

        assert result == {"file1.py", "file2.py"}


class TestGetFileChangeSizes:
    def test_get_file_change_sizes_normal(self):
        """Test getting file change sizes for normal files"""
        mock_repo = Mock(spec=git.Repo)
        mock_repo.git.diff.return_value = "10\t5\tfile1.py\n20\t15\tfile2.py\n0\t0\tfile3.py"

        result = get_file_change_sizes(mock_repo)

        assert result == {
            "file1.py": 15,  # 10 + 5
            "file2.py": 35,  # 20 + 15
            "file3.py": 0,  # 0 + 0
        }
        mock_repo.git.diff.assert_called_once_with("--cached", "--numstat", "-M")

    def test_get_file_change_sizes_binary_files(self):
        """Test getting file change sizes for binary files"""
        mock_repo = Mock(spec=git.Repo)
        mock_repo.git.diff.return_value = "10\t5\tfile1.py\n-\t-\tbinary_file.jpg\n20\t15\tfile2.py"

        result = get_file_change_sizes(mock_repo)

        assert result == {
            "file1.py": 15,
            "binary_file.jpg": 0,
            "file2.py": 35,
        }

    def test_get_file_change_sizes_empty(self):
        """Test getting file change sizes when no files changed"""
        mock_repo = Mock(spec=git.Repo)
        mock_repo.git.diff.return_value = ""

        result = get_file_change_sizes(mock_repo)

        assert result == {}

    def test_get_file_change_sizes_invalid_format(self):
        """Test handling invalid numstat format"""
        mock_repo = Mock(spec=git.Repo)
        mock_repo.git.diff.return_value = "10\t5\tfile1.py\ninvalid_line\n20\t15\tfile2.py"

        result = get_file_change_sizes(mock_repo)

        assert result == {
            "file1.py": 15,
            "file2.py": 35,
        }


class TestGetFilteredDiffFiles:
    @patch("tgit.commit.get_changed_files_from_status")
    @patch("tgit.commit.get_file_change_sizes")
    def test_get_filtered_diff_files_large_files(self, mock_get_sizes, mock_get_changed):
        """Test filtering out large files"""
        mock_repo = Mock(spec=git.Repo)
        mock_get_changed.return_value = {"small_file.py", "large_file.py"}
        mock_get_sizes.return_value = {
            "small_file.py": 100,
            "large_file.py": MAX_DIFF_LINES + 1,
        }

        files_to_include, lock_files = get_filtered_diff_files(mock_repo)

        assert files_to_include == ["small_file.py"]
        assert lock_files == []


class TestOpenAIIntegration:
    def test_import_openai_success(self):
        """Test successful OpenAI import"""
        with patch("importlib.import_module") as mock_import:
            mock_openai = Mock()
            mock_import.return_value = mock_openai

            result = _import_openai()

            assert result == mock_openai
            mock_import.assert_called_once_with("openai")

    def test_import_openai_failure(self):
        """Test OpenAI import failure"""
        with patch("importlib.import_module") as mock_import:
            mock_import.side_effect = ImportError("No module named 'openai'")

            with pytest.raises(ImportError, match="openai package is not installed"):
                _import_openai()

    def test_check_openai_availability_success(self):
        """Test OpenAI availability check success"""
        with patch("tgit.commit._import_openai") as mock_import:
            mock_import.return_value = Mock()

            # Should not raise
            _check_openai_availability()

            mock_import.assert_called_once()

    def test_check_openai_availability_failure(self):
        """Test OpenAI availability check failure"""
        with patch("tgit.commit._import_openai") as mock_import:
            mock_import.side_effect = ImportError("openai package is not installed")

            with pytest.raises(ImportError):
                _check_openai_availability()
