"""Tests for commit module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import git
from pathlib import Path
import tempfile
from click.testing import CliRunner

from tgit.commit import (
    CommitArgs,
    CommitData,
    TemplateParams,
    get_changed_files_from_status,
    get_file_change_sizes,
    get_filtered_diff_files,
    _import_openai,
    _check_openai_availability,
    _create_openai_client,
    _generate_commit_with_ai,
    get_ai_command,
    handle_commit,
    commit,
    MAX_DIFF_LINES,
    NUMSTAT_PARTS,
    NAME_STATUS_PARTS,
    RENAME_STATUS_PARTS,
)


class TestCommitArgs:
    """Test CommitArgs dataclass."""

    def test_commit_args_creation(self):
        """Test creating CommitArgs instance."""
        args = CommitArgs(message=["feat", "add new feature"], emoji=True, breaking=False, ai=False)
        assert args.message == ["feat", "add new feature"]
        assert args.emoji is True
        assert args.breaking is False
        assert args.ai is False


class TestTemplateParams:
    """Test TemplateParams dataclass."""

    def test_template_params_creation(self):
        """Test creating TemplateParams instance."""
        params = TemplateParams(types=["feat", "fix"], branch="main", specified_type="feat")
        assert params.types == ["feat", "fix"]
        assert params.branch == "main"
        assert params.specified_type == "feat"

    def test_template_params_default_specified_type(self):
        """Test TemplateParams with default specified_type."""
        params = TemplateParams(types=["feat", "fix"], branch="develop")
        assert params.specified_type is None


class TestCommitData:
    """Test CommitData Pydantic model."""

    def test_commit_data_creation(self):
        """Test creating CommitData instance."""
        data = CommitData(type="feat", scope="auth", msg="add login functionality", is_breaking=False)
        assert data.type == "feat"
        assert data.scope == "auth"
        assert data.msg == "add login functionality"
        assert data.is_breaking is False

    def test_commit_data_with_none_scope(self):
        """Test CommitData with None scope."""
        data = CommitData(type="fix", scope=None, msg="fix bug", is_breaking=False)
        assert data.scope is None


class TestGetChangedFilesFromStatus:
    """Test get_changed_files_from_status function."""

    def test_get_changed_files_modified_files(self):
        """Test getting changed files with modified files."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = "M\tsrc/file1.py\nA\tsrc/file2.py\nD\tsrc/file3.py"

        result = get_changed_files_from_status(mock_repo)

        assert result == {"src/file1.py", "src/file2.py", "src/file3.py"}
        mock_repo.git.diff.assert_called_once_with("--cached", "--name-status", "-M")

    def test_get_changed_files_renamed_files(self):
        """Test getting changed files with renamed files."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = "R100\told_file.py\tnew_file.py\nM\tsrc/file1.py"

        result = get_changed_files_from_status(mock_repo)

        assert result == {"old_file.py", "new_file.py", "src/file1.py"}

    def test_get_changed_files_empty_diff(self):
        """Test getting changed files with empty diff."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = ""

        result = get_changed_files_from_status(mock_repo)

        assert result == set()

    def test_get_changed_files_malformed_lines(self):
        """Test handling malformed lines in diff output."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = "M\nincomplete_line\nA\tsrc/file.py"

        result = get_changed_files_from_status(mock_repo)

        assert result == {"src/file.py"}


class TestGetFileChangeSizes:
    """Test get_file_change_sizes function."""

    def test_get_file_change_sizes_normal_files(self):
        """Test getting file change sizes for normal files."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = "10\t5\tsrc/file1.py\n20\t0\tsrc/file2.py\n0\t15\tsrc/file3.py"

        result = get_file_change_sizes(mock_repo)

        expected = {"src/file1.py": 15, "src/file2.py": 20, "src/file3.py": 15}
        assert result == expected
        mock_repo.git.diff.assert_called_once_with("--cached", "--numstat", "-M")

    def test_get_file_change_sizes_binary_files(self):
        """Test getting file change sizes for binary files."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = "-\t-\timage.png\n5\t3\tsrc/file.py"

        result = get_file_change_sizes(mock_repo)

        expected = {"image.png": 0, "src/file.py": 8}
        assert result == expected

    def test_get_file_change_sizes_empty_diff(self):
        """Test getting file change sizes with empty diff."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = ""

        result = get_file_change_sizes(mock_repo)

        assert result == {}

    def test_get_file_change_sizes_malformed_lines(self):
        """Test handling malformed lines in numstat output."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = "invalid_line\n10\t5\tsrc/file.py\nincomplete"

        result = get_file_change_sizes(mock_repo)

        assert result == {"src/file.py": 15}


class TestGetFilteredDiffFiles:
    """Test get_filtered_diff_files function."""

    @patch("tgit.commit.get_changed_files_from_status")
    @patch("tgit.commit.get_file_change_sizes")
    def test_get_filtered_diff_files_normal_files(self, mock_get_sizes, mock_get_files):
        """Test filtering diff files with normal files."""
        mock_get_files.return_value = {"src/file1.py", "src/file2.py", "package.lock"}
        mock_get_sizes.return_value = {"src/file1.py": 100, "src/file2.py": 50}

        mock_repo = Mock()
        files_to_include, lock_files = get_filtered_diff_files(mock_repo)

        assert files_to_include == ["src/file1.py", "src/file2.py"]
        assert lock_files == ["package.lock"]

    @patch("tgit.commit.get_changed_files_from_status")
    @patch("tgit.commit.get_file_change_sizes")
    def test_get_filtered_diff_files_large_files(self, mock_get_sizes, mock_get_files):
        """Test filtering out large files."""
        mock_get_files.return_value = {"src/small.py", "src/large.py"}
        mock_get_sizes.return_value = {"src/small.py": 100, "src/large.py": MAX_DIFF_LINES + 1}

        mock_repo = Mock()
        files_to_include, lock_files = get_filtered_diff_files(mock_repo)

        assert files_to_include == ["src/small.py"]
        assert lock_files == []

    @patch("tgit.commit.get_changed_files_from_status")
    @patch("tgit.commit.get_file_change_sizes")
    def test_get_filtered_diff_files_no_size_info(self, mock_get_sizes, mock_get_files):
        """Test filtering files without size information."""
        mock_get_files.return_value = {"src/file1.py", "src/file2.py"}
        mock_get_sizes.return_value = {"src/file1.py": 100}  # Missing file2.py

        mock_repo = Mock()
        files_to_include, lock_files = get_filtered_diff_files(mock_repo)

        assert files_to_include == ["src/file1.py", "src/file2.py"]  # file2.py included with size 0
        assert lock_files == []


class TestOpenAIImport:
    """Test OpenAI import functions."""

    @patch("tgit.commit.importlib.import_module")
    def test_import_openai_success(self, mock_import):
        """Test successful OpenAI import."""
        mock_openai = Mock()
        mock_import.return_value = mock_openai

        result = _import_openai()

        assert result == mock_openai
        mock_import.assert_called_once_with("openai")

    @patch("tgit.commit.importlib.import_module")
    def test_import_openai_failure(self, mock_import):
        """Test OpenAI import failure."""
        mock_import.side_effect = ImportError("No module named 'openai'")

        with pytest.raises(ImportError, match="openai package is not installed"):
            _import_openai()

    @patch("tgit.commit._import_openai")
    def test_check_openai_availability_success(self, mock_import):
        """Test checking OpenAI availability successfully."""
        mock_import.return_value = Mock()

        # Should not raise an exception
        _check_openai_availability()

        mock_import.assert_called_once()

    @patch("tgit.commit._import_openai")
    def test_check_openai_availability_failure(self, mock_import):
        """Test checking OpenAI availability failure."""
        mock_import.side_effect = ImportError("openai package is not installed")

        with pytest.raises(ImportError):
            _check_openai_availability()


class TestCreateOpenAIClient:
    """Test OpenAI client creation."""

    @patch("tgit.commit._import_openai")
    @patch("tgit.commit.settings")
    def test_create_openai_client_default(self, mock_settings, mock_import):
        """Test creating OpenAI client with default settings."""
        mock_openai = Mock()
        mock_client = Mock()
        mock_openai.Client.return_value = mock_client
        mock_import.return_value = mock_openai

        mock_settings.api_url = None
        mock_settings.api_key = None

        result = _create_openai_client()

        assert result == mock_client
        mock_openai.Client.assert_called_once()

    @patch("tgit.commit._import_openai")
    @patch("tgit.commit.settings")
    def test_create_openai_client_custom_settings(self, mock_settings, mock_import):
        """Test creating OpenAI client with custom settings."""
        mock_openai = Mock()
        mock_client = Mock()
        mock_openai.Client.return_value = mock_client
        mock_import.return_value = mock_openai

        mock_settings.api_url = "https://api.example.com"
        mock_settings.api_key = "test-key"

        result = _create_openai_client()

        assert result == mock_client
        mock_openai.Client.assert_called_once_with(api_key="test-key", base_url="https://api.example.com")


class TestGenerateCommitWithAI:
    """Test AI commit generation."""

    @patch("tgit.commit._check_openai_availability")
    @patch("tgit.commit._create_openai_client")
    @patch("tgit.commit.console")
    @patch("tgit.commit.commit_prompt_template")
    @patch("tgit.commit.settings")
    def test_generate_commit_with_ai_success(self, mock_settings, mock_template, mock_console, mock_create_client, mock_check):
        """Test successful AI commit generation."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        mock_template.render.return_value = "system prompt"
        mock_settings.model = "gpt-4"

        # Mock the response
        mock_response = Mock()
        mock_commit_data = CommitData(type="feat", scope="auth", msg="add login", is_breaking=False)
        mock_response.output_parsed = mock_commit_data
        mock_client.responses.parse.return_value = mock_response

        result = _generate_commit_with_ai("diff content", "feat", "main")

        assert result == mock_commit_data
        mock_check.assert_called_once()
        mock_create_client.assert_called_once()
        mock_client.responses.parse.assert_called_once()

    @patch("tgit.commit._check_openai_availability")
    @patch("tgit.commit._create_openai_client")
    @patch("tgit.commit.console")
    def test_generate_commit_with_ai_failure(self, mock_console, mock_create_client, mock_check):
        """Test AI commit generation failure."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        mock_client.responses.parse.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            _generate_commit_with_ai("diff content", None, "main")


class TestGetAICommand:
    """Test get_ai_command function."""

    @patch("tgit.commit.Path.cwd")
    @patch("tgit.commit.git.Repo")
    def test_get_ai_command_not_git_repo(self, mock_repo, mock_cwd):
        """Test get_ai_command when not in git repo."""
        mock_cwd.return_value = Path(tempfile.gettempdir())
        mock_repo.side_effect = git.InvalidGitRepositoryError("Not a git repo")

        with patch("tgit.commit.print") as mock_print:
            result = get_ai_command()

            assert result is None
            mock_print.assert_called_once_with("[yellow]Not a git repository[/yellow]")

    @patch("tgit.commit.Path.cwd")
    @patch("tgit.commit.git.Repo")
    @patch("tgit.commit.get_filtered_diff_files")
    def test_get_ai_command_no_files(self, mock_get_files, mock_repo, mock_cwd):
        """Test get_ai_command when no files to commit."""
        mock_cwd.return_value = Path(tempfile.gettempdir())
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_get_files.return_value = ([], [])

        with patch("tgit.commit.print") as mock_print:
            result = get_ai_command()

            assert result is None
            mock_print.assert_called_once_with("[yellow]No files to commit, please add some files before using AI[/yellow]")

    @patch("tgit.commit.Path.cwd")
    @patch("tgit.commit.git.Repo")
    @patch("tgit.commit.get_filtered_diff_files")
    @patch("tgit.commit._generate_commit_with_ai")
    @patch("tgit.commit.get_commit_command")
    @patch("tgit.commit.settings")
    def test_get_ai_command_success(self, mock_settings, mock_get_commit_command, mock_generate, mock_get_files, mock_repo, mock_cwd):
        """Test successful get_ai_command."""
        mock_cwd.return_value = Path(tempfile.gettempdir())
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_get_files.return_value = (["src/file.py"], ["package.lock"])

        mock_repo_instance.git.diff.return_value = "diff content"
        mock_repo_instance.active_branch.name = "main"
        mock_settings.commit.emoji = True

        mock_commit_data = CommitData(type="feat", scope="auth", msg="add login", is_breaking=False)
        mock_generate.return_value = mock_commit_data
        mock_get_commit_command.return_value = "git commit -m 'feat(auth): add login'"

        result = get_ai_command()

        assert result == "git commit -m 'feat(auth): add login'"
        mock_generate.assert_called_once()
        mock_get_commit_command.assert_called_once_with("feat", "auth", "add login", use_emoji=True, is_breaking=False)

    @patch("tgit.commit.Path.cwd")
    @patch("tgit.commit.git.Repo")
    @patch("tgit.commit.get_filtered_diff_files")
    @patch("tgit.commit._generate_commit_with_ai")
    def test_get_ai_command_ai_failure(self, mock_generate, mock_get_files, mock_repo, mock_cwd):
        """Test get_ai_command when AI generation fails."""
        mock_cwd.return_value = Path(tempfile.gettempdir())
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_get_files.return_value = (["src/file.py"], [])

        mock_repo_instance.git.diff.return_value = "diff content"
        mock_repo_instance.active_branch.name = "main"
        mock_generate.side_effect = Exception("AI Error")

        with patch("tgit.commit.print") as mock_print:
            result = get_ai_command()

            assert result is None
            mock_print.assert_any_call("[red]Could not connect to AI provider[/red]")


class TestHandleCommit:
    """Test handle_commit function."""

    @patch("tgit.commit.get_ai_command")
    @patch("tgit.commit.run_command")
    def test_handle_commit_ai_mode(self, mock_run_command, mock_get_ai_command):
        """Test handle_commit in AI mode."""
        mock_get_ai_command.return_value = "git commit -m 'feat: add feature'"

        args = CommitArgs(message=[], emoji=False, breaking=False, ai=True)
        handle_commit(args)

        mock_get_ai_command.assert_called_once_with()
        # run_command is called with settings and command
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args[0]
        assert len(call_args) == 2
        assert call_args[1] == "git commit -m 'feat: add feature'"

    @patch("tgit.commit.get_ai_command")
    @patch("tgit.commit.run_command")
    def test_handle_commit_no_message(self, mock_run_command, mock_get_ai_command):
        """Test handle_commit with no message (fallback to AI)."""
        mock_get_ai_command.return_value = "git commit -m 'feat: add feature'"

        args = CommitArgs(message=[], emoji=False, breaking=False, ai=False)
        handle_commit(args)

        mock_get_ai_command.assert_called_once_with()
        # run_command is called with settings and command
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args[0]
        assert len(call_args) == 2
        assert call_args[1] == "git commit -m 'feat: add feature'"

    @patch("tgit.commit.get_ai_command")
    @patch("tgit.commit.run_command")
    def test_handle_commit_single_message_valid_type(self, mock_run_command, mock_get_ai_command):
        """Test handle_commit with single message (valid type)."""
        mock_get_ai_command.return_value = "git commit -m 'feat: add feature'"

        args = CommitArgs(message=["feat"], emoji=False, breaking=False, ai=False)
        handle_commit(args)

        mock_get_ai_command.assert_called_once_with(specified_type="feat")
        # run_command is called with settings and command
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args[0]
        assert len(call_args) == 2
        assert call_args[1] == "git commit -m 'feat: add feature'"

    def test_handle_commit_single_message_invalid_type(self):
        """Test handle_commit with single message (invalid type)."""
        args = CommitArgs(message=["invalid"], emoji=False, breaking=False, ai=False)

        with patch("tgit.commit.print") as mock_print:
            handle_commit(args)

            mock_print.assert_any_call("Invalid type: invalid")

    @patch("tgit.commit.get_commit_command")
    @patch("tgit.commit.run_command")
    @patch("tgit.commit.settings")
    def test_handle_commit_full_message(self, mock_settings, mock_run_command, mock_get_commit_command):
        """Test handle_commit with full message."""
        mock_settings.commit.emoji = False
        mock_get_commit_command.return_value = "git commit -m 'feat: add feature'"

        args = CommitArgs(message=["feat", "add feature"], emoji=False, breaking=False, ai=False)
        handle_commit(args)

        mock_get_commit_command.assert_called_once_with("feat", None, "add feature", use_emoji=False, is_breaking=False)
        # run_command is called with settings and command
        mock_run_command.assert_called_once_with(mock_settings, "git commit -m 'feat: add feature'")

    @patch("tgit.commit.get_commit_command")
    @patch("tgit.commit.run_command")
    @patch("tgit.commit.settings")
    def test_handle_commit_with_scope(self, mock_settings, mock_run_command, mock_get_commit_command):
        """Test handle_commit with scope."""
        mock_settings.commit.emoji = False
        mock_get_commit_command.return_value = "git commit -m 'feat(auth): add login'"

        args = CommitArgs(message=["feat", "auth", "add", "login"], emoji=False, breaking=False, ai=False)
        handle_commit(args)

        mock_get_commit_command.assert_called_once_with("feat", "auth", "add login", use_emoji=False, is_breaking=False)
        # run_command is called with settings and command
        mock_run_command.assert_called_once_with(mock_settings, "git commit -m 'feat(auth): add login'")

    @patch("tgit.commit.get_commit_command")
    @patch("tgit.commit.run_command")
    @patch("tgit.commit.settings")
    def test_handle_commit_with_emoji_override(self, mock_settings, mock_run_command, mock_get_commit_command):
        """Test handle_commit with emoji override."""
        mock_settings.commit.emoji = False
        mock_get_commit_command.return_value = "git commit -m '✨ feat: add feature'"

        args = CommitArgs(message=["feat", "add feature"], emoji=True, breaking=False, ai=False)
        handle_commit(args)

        mock_get_commit_command.assert_called_once_with("feat", None, "add feature", use_emoji=True, is_breaking=False)
        # run_command is called with settings and command
        mock_run_command.assert_called_once_with(mock_settings, "git commit -m '✨ feat: add feature'")

    def test_handle_commit_invalid_type_in_full_message(self):
        """Test handle_commit with invalid type in full message."""
        args = CommitArgs(message=["invalid", "message"], emoji=False, breaking=False, ai=False)

        with patch("tgit.commit.print") as mock_print:
            handle_commit(args)

            mock_print.assert_any_call("Invalid type: invalid")


class TestCommitFunction:
    """Test the main commit function."""

    @patch("tgit.commit.handle_commit")
    def test_commit_function_default_args(self, mock_handle_commit):
        """Test commit function with default arguments."""
        runner = CliRunner()
        result = runner.invoke(commit, [])

        assert result.exit_code == 0
        # Check that handle_commit was called once
        mock_handle_commit.assert_called_once()

        # Get the actual args passed to handle_commit - it should be a CommitArgs object
        called_args = mock_handle_commit.call_args[0][0]
        assert hasattr(called_args, "message")
        assert hasattr(called_args, "emoji")
        assert hasattr(called_args, "breaking")
        assert hasattr(called_args, "ai")

    @patch("tgit.commit.handle_commit")
    def test_commit_function_with_args(self, mock_handle_commit):
        """Test commit function with custom arguments."""
        runner = CliRunner()
        result = runner.invoke(commit, ["feat", "add feature", "--emoji", "--breaking", "--ai"])

        assert result.exit_code == 0
        expected_args = CommitArgs(message=["feat", "add feature"], emoji=True, breaking=True, ai=True)
        mock_handle_commit.assert_called_once()

        # Check the args passed to handle_commit
        called_args = mock_handle_commit.call_args[0][0]
        assert called_args.message == expected_args.message
        assert called_args.emoji == expected_args.emoji
        assert called_args.breaking == expected_args.breaking
        assert called_args.ai == expected_args.ai


class TestCommitErrorHandling:
    """Test error handling in commit functions."""

    @patch("tgit.commit.get_ai_command")
    def test_handle_commit_no_message(self, mock_get_ai_command):
        """Test handle_commit with no message provided."""
        args = CommitArgs(message=[], emoji=False, breaking=False, ai=False)

        # Mock get_ai_command to return None (no AI command generated)
        mock_get_ai_command.return_value = None

        # This should call get_ai_command and return early when it returns None
        handle_commit(args)

        # Should have called get_ai_command
        mock_get_ai_command.assert_called_once()

    def test_get_file_change_sizes_binary_files(self):
        """Test get_file_change_sizes with binary files."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = "-\t-\timage.png\n5\t0\tfile.py\n-\t-\tbinary.dat"

        result = get_file_change_sizes(mock_repo)

        # Should handle binary files (marked with -/-) as 0 size
        expected = {
            "image.png": 0,  # Binary files treated as 0 size
            "file.py": 5,
            "binary.dat": 0,
        }
        assert result == expected

    @patch("tgit.commit.git.Repo")
    def test_get_changed_files_from_status_renamed_files(self, mock_repo_class):
        """Test get_changed_files_from_status with renamed files."""
        mock_repo = Mock()
        mock_repo.git.diff.return_value = """R100\told_name.py\tnew_name.py
R100\tdir/old.js\tdir/new.js
M\tmodified.py"""

        result = get_changed_files_from_status(mock_repo)

        # Should include both old and new names of renamed files and modified files
        expected = {"old_name.py", "new_name.py", "dir/old.js", "dir/new.js", "modified.py"}
        assert result == expected
