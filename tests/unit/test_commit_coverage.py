from unittest.mock import Mock, patch

import pytest
from tgit.commit import (
    CommitArgs,
    CommitData,
    PotentialSecret,
    _build_litellm_model_name,
    _confirm_detected_secrets,
    _get_changed_files_from_status_output,
    _generate_commit_with_ai,
    _resolve_api_key,
    _resolve_base_url,
    _split_diff_sections,
    _supports_reasoning,
    _truncate_diff_section,
    _truncate_large_diff_sections,
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

    def test_split_diff_sections_single_file(self):
        """Test _split_diff_sections with a single-file diff (no second diff header)."""
        diff = """diff --git a/file.py b/file.py
--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
 line1
+line2
 line3"""
        sections = _split_diff_sections(diff)
        assert len(sections) == 1
        assert "diff --git a/file.py" in sections[0]

    def test_split_diff_sections_multi_file(self):
        """Test _split_diff_sections with multi-file diff."""
        diff = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1 +1,2 @@
 a
+new

 NOT_A_DIFF_HEADER
diff --git a/b.py b/b.py
--- a/b.py
+++ b/b.py
@@ -1 +1,2 @@
 b
+new2"""
        sections = _split_diff_sections(diff)
        assert len(sections) == 2

    def test_split_diff_sections_empty(self):
        """Test _split_diff_sections with empty input."""
        assert _split_diff_sections("") == []
        assert _split_diff_sections(None) == []

    def test_truncate_diff_section_within_limits(self):
        """Test _truncate_diff_section when section is within limits."""
        small_diff = "diff --git a/small.py b/small.py\n+small change"
        result = _truncate_diff_section(small_diff)
        assert result == small_diff
        assert "[INFO]" not in result

    def test_truncate_diff_section_exact_boundary(self):
        """Test _truncate_diff_section when omitted_chars <= 0."""
        # Create a diff exactly at the boundary where head+tail >= total
        from tgit.commit import TRUNCATED_DIFF_HEAD_CHARS, TRUNCATED_DIFF_TAIL_CHARS, MAX_DIFF_SECTION_CHARS

        # Use a diff that's big in char count but small in lines
        with patch("tgit.commit.MAX_DIFF_SECTION_CHARS", 50):
            with patch("tgit.commit.MAX_DIFF_LINES", 1000):
                diff = "x" * 60  # > MAX_DIFF_SECTION_CHARS, but head+tail covers it
                result = _truncate_diff_section(diff)
                # Should still return original since omitted <= 0 or no truncation
                assert len(result) == 60

    def test_truncate_large_diff_sections_no_sections(self):
        """Test _truncate_large_diff_sections with no file sections."""
        diff = "just some text without diff headers"
        result = _truncate_large_diff_sections(diff)
        assert result == diff

    @patch("tgit.commit.settings")
    def test_resolve_api_key_from_deepseek_env(self, mock_settings):
        """Test _resolve_api_key resolves from DeepSeek env var."""
        mock_settings.api_key = ""
        mock_settings.provider = "deepseek"

        with patch("tgit.commit.os.getenv", return_value="sk-deepseek-env"):
            result = _resolve_api_key()
            assert result == "sk-deepseek-env"

    @patch("tgit.commit.settings")
    def test_resolve_base_url_from_settings_override(self, mock_settings):
        """Test _resolve_base_url returns settings URL even with provider preset."""
        mock_settings.api_url = "https://custom-proxy.example.com"
        mock_settings.provider = "openai"

        result = _resolve_base_url()
        assert result == "https://custom-proxy.example.com"

    @patch("tgit.commit.settings")
    @patch("tgit.commit.os.getenv")
    def test_resolve_api_key_unknown_provider(self, mock_getenv, mock_settings):
        """Test _resolve_api_key with provider not in presets."""
        mock_settings.api_key = ""
        mock_settings.provider = "custom"

        result = _resolve_api_key()
        assert result is None
        mock_getenv.assert_not_called()

    @patch("tgit.commit.settings")
    def test_build_litellm_model_name_custom_provider(self, mock_settings):
        """Test _build_litellm_model_name with a provider not in the prefix map."""
        mock_settings.provider = "custom-provider"

        result = _build_litellm_model_name("my-model")
        assert result == "custom-provider/my-model"

    def test_get_changed_files_from_status_output_malformed_short_line(self):
        """Test malformed status line shorter than NAME_STATUS_PARTS + 1."""
        # NAME_STATUS_PARTS = 2, so lines < 3 chars are skipped
        status_output = "\n\nM  valid.py"
        result = _get_changed_files_from_status_output(status_output)
        # Empty/blank lines should be skipped
        assert "valid.py" in result
        assert len(result) == 1

    @patch("tgit.commit.commit_prompt_template")
    @patch("tgit.commit.settings")
    @patch("tgit.commit._resolve_api_key")
    @patch("tgit.commit._resolve_base_url")
    def test_generate_commit_with_ai_empty_choices_fallback(
        self, mock_resolve_url, mock_resolve_key, mock_settings, mock_template
    ):
        """Test fallback when response has empty choices."""
        mock_template.render.return_value = "system prompt"
        mock_settings.model = "gpt-4o"
        mock_settings.provider = "auto"
        mock_settings.reasoning_effort = ""
        mock_resolve_key.return_value = None
        mock_resolve_url.return_value = None

        mock_response = Mock()
        mock_response.choices = []  # Empty choices

        with patch.dict("sys.modules", {"litellm": Mock()}):
            import sys
            sys.modules["litellm"].completion.return_value = mock_response
            result = _generate_commit_with_ai("diff content", None, "main")

        assert result is None

    @patch("tgit.commit.commit_prompt_template")
    @patch("tgit.commit.settings")
    @patch("tgit.commit._resolve_api_key")
    @patch("tgit.commit._resolve_base_url")
    def test_generate_commit_with_ai_empty_content_fallback(
        self, mock_resolve_url, mock_resolve_key, mock_settings, mock_template
    ):
        """Test fallback when response has empty content."""
        mock_template.render.return_value = "system prompt"
        mock_settings.model = "gpt-4o"
        mock_settings.provider = "auto"
        mock_settings.reasoning_effort = ""
        mock_resolve_key.return_value = None
        mock_resolve_url.return_value = None

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = ""

        with patch.dict("sys.modules", {"litellm": Mock()}):
            import sys
            sys.modules["litellm"].completion.return_value = mock_response
            result = _generate_commit_with_ai("diff content", None, "main")

        assert result is None

    @patch("tgit.commit.click.confirm")
    def test_confirm_detected_secrets_warning_only(self, mock_confirm):
        """Test _confirm_detected_secrets with only warning-level secrets."""
        mock_confirm.return_value = True
        secrets = [
            PotentialSecret(file="config.py", description="API_KEY variable name", level="warning"),
        ]

        with patch("tgit.commit.print") as mock_print:
            result = _confirm_detected_secrets(secrets)

        assert result is True
        mock_print.assert_any_call("[yellow]Detected potential sensitive key names (no values):[/yellow]")
        mock_confirm.assert_called_once_with("Detected potential sensitive key names. Continue with commit?", default=True)

    @patch("tgit.commit.click.confirm")
    def test_confirm_detected_secrets_no_secrets(self, mock_confirm):
        """Test _confirm_detected_secrets with empty secrets list."""
        result = _confirm_detected_secrets([])
        assert result is True
        mock_confirm.assert_not_called()

    @patch("tgit.commit.git.Repo")
    @patch("tgit.commit._stage_all_changes_if_confirmed")
    @patch("tgit.commit.get_filtered_diff_files")
    def test_get_ai_command_no_diff(self, mock_filter, mock_stage_all, mock_repo):
        """Test get_ai_command when there is no diff after filtering."""
        repo = Mock()
        mock_repo.return_value = repo
        mock_stage_all.return_value = True

        # Return some files to pass the first check
        mock_filter.return_value = (["file.txt"], [])

        # But make git diff return empty string
        repo.git.diff.return_value = ""
        repo.active_branch.name = "main"

        assert get_ai_command() is None

    @patch("tgit.commit.git.Repo")
    @patch("tgit.commit._stage_all_changes_if_confirmed")
    @patch("tgit.commit.get_filtered_diff_files")
    @patch("tgit.commit._generate_commit_with_ai")
    def test_get_ai_command_ai_failure(self, mock_gen, mock_filter, mock_stage_all, mock_repo):
        """Test get_ai_command when AI generation fails."""
        repo = Mock()
        mock_repo.return_value = repo
        mock_stage_all.return_value = True
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

    @patch("tgit.commit._stage_all_changes_if_confirmed")
    @patch("tgit.commit._get_repo_for_ai")
    @patch("tgit.commit.get_commit_command")
    @patch("tgit.commit.run_command")
    def test_handle_commit_manual_repo_none(
        self, mock_run, mock_get_cmd, mock_get_repo, mock_stage
    ):
        """Test handle_commit manual path when repo is None."""
        mock_get_cmd.return_value = "git commit -m 'feat: test'"
        mock_get_repo.return_value = None

        args = CommitArgs(message=["feat", "test"], emoji=False, breaking=False, ai=False)
        handle_commit(args)

        mock_run.assert_not_called()

    @patch("tgit.commit._stage_all_changes_if_confirmed")
    @patch("tgit.commit._get_repo_for_ai")
    @patch("tgit.commit.get_commit_command")
    @patch("tgit.commit.run_command")
    def test_handle_commit_manual_stage_declined(
        self, mock_run, mock_get_cmd, mock_get_repo, mock_stage
    ):
        """Test handle_commit manual path when staging is declined."""
        mock_get_cmd.return_value = "git commit -m 'feat: test'"
        mock_get_repo.return_value = Mock()
        mock_stage.return_value = False

        args = CommitArgs(message=["feat", "test"], emoji=False, breaking=False, ai=False)
        handle_commit(args)

        mock_run.assert_not_called()

    @patch("tgit.commit.get_ai_command")
    @patch("tgit.commit.run_command")
    @patch("tgit.commit.settings")
    def test_handle_commit_ai_mode_none_result(self, mock_settings, mock_run, mock_get_ai):
        """Test handle_commit AI mode when get_ai_command returns None."""
        mock_get_ai.return_value = None

        args = CommitArgs(message=[], emoji=False, breaking=False, ai=True)
        handle_commit(args)

        mock_run.assert_not_called()
