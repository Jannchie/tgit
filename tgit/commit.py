import importlib.resources
import itertools
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click
import git
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field
from rich import get_console, print

from tgit.constants import (
    DEFAULT_MODEL,
    OPENAI_REASONING_MODEL_HINTS,
    PROVIDER_PRESETS,
)
from tgit.shared import settings
from tgit.utils import get_commit_command, run_command, type_emojis

console = get_console()
with importlib.resources.path("tgit", "prompts") as prompt_path:
    env = Environment(loader=FileSystemLoader(prompt_path), autoescape=True)

commit_types = ["feat", "fix", "chore", "docs", "style", "refactor", "perf", "test", "ci"]
commit_file = "commit.txt"
commit_prompt_template = env.get_template("commit.txt")

# Define click arguments/options at module level to avoid B008
MESSAGE_ARG = click.argument(
    "message",
    nargs=-1,
    required=False,
)
EMOJI_OPT = click.option("-e", "--emoji", is_flag=True, help="use emojis")
BREAKING_OPT = click.option("-b", "--breaking", is_flag=True, help="breaking change")
AI_OPT = click.option("-a", "--ai", is_flag=True, help="use ai")

MAX_DIFF_LINES = 1000
MAX_DIFF_SECTION_CHARS = 20000
TRUNCATED_DIFF_HEAD_CHARS = 6000
TRUNCATED_DIFF_TAIL_CHARS = 4000
NUMSTAT_PARTS = 3
NAME_STATUS_PARTS = 2
RENAME_STATUS_PARTS = 3
SENSITIVITY_LEVEL_WARNING = "warning"
SENSITIVITY_LEVEL_ERROR = "error"


# Initialize commit types from settings
commit_type_list = ["feat", "fix", "chore", "docs", "style", "refactor", "perf"]
for commit_type_obj in settings.commit.types:
    if commit_type_obj.emoji and commit_type_obj.type:
        type_emojis[commit_type_obj.type] = commit_type_obj.emoji
        commit_type_list.append(commit_type_obj.type)


@dataclass
class CommitArgs:
    message: list[str]
    emoji: bool
    breaking: bool
    ai: bool


@dataclass
class TemplateParams:
    types: list[str]
    branch: str
    specified_type: str | None = None


class PotentialSecret(BaseModel):
    file: str
    description: str
    level: str = SENSITIVITY_LEVEL_ERROR


class CommitData(BaseModel):
    type: str
    scope: str | None = None
    msg: str
    is_breaking: bool = False
    secrets: list[PotentialSecret] = Field(default_factory=list)


def _supports_reasoning(model: str) -> bool:
    """Return True when the selected model supports OpenAI reasoning parameters."""
    if not model:
        return False
    if settings.provider not in {"openai", "auto"}:
        return False
    model_lower = model.lower()
    return any(hint in model_lower for hint in OPENAI_REASONING_MODEL_HINTS)


def _build_litellm_model_name(model: str) -> str:
    """Build the litellm model name with provider prefix if needed."""
    provider = settings.provider
    if not provider or provider == "auto":
        return model
    # Map provider to litellm prefix
    provider_prefix_map = {
        "openai": "openai",
        "deepseek": "deepseek",
        "anthropic": "anthropic",
        "google": "gemini",
        "gemini": "gemini",
    }
    prefix = provider_prefix_map.get(provider, provider)
    # Don't double-prefix if model already has a prefix
    if "/" in model:
        return model
    return f"{prefix}/{model}"


def get_changed_files_from_status(repo: git.Repo) -> set[str]:
    """获取所有变更的文件，包括重命名/移动的文件"""
    diff_name_status = repo.git.diff("--cached", "--name-status", "-M")
    all_changed_files: set[str] = set()

    for line in diff_name_status.splitlines():
        parts = line.split("\t")
        if len(parts) >= NAME_STATUS_PARTS:
            status = parts[0]
            if status.startswith("R"):  # 重命名/移动
                # 重命名格式: R100    old_file    new_file
                if len(parts) >= RENAME_STATUS_PARTS:
                    old_file, new_file = parts[1], parts[2]
                    all_changed_files.add(old_file)
                    all_changed_files.add(new_file)
            else:
                # 其他状态: A(添加), M(修改), D(删除)等
                filename = parts[1]
                all_changed_files.add(filename)

    return all_changed_files


def get_file_change_sizes(repo: git.Repo) -> dict[str, int]:
    """获取文件变更的行数统计"""
    diff_numstat = repo.git.diff("--cached", "--numstat", "-M")
    file_sizes: dict[str, int] = {}

    for line in diff_numstat.splitlines():
        parts = line.split("\t")
        if len(parts) >= NUMSTAT_PARTS:
            added, deleted, filename = parts[0], parts[1], parts[2]
            try:
                added_int = int(added) if added != "-" else 0
                deleted_int = int(deleted) if deleted != "-" else 0
                file_sizes[filename] = added_int + deleted_int
            except ValueError:
                # 对于二进制文件等特殊情况，设置为0以包含在diff中
                file_sizes[filename] = 0

    return file_sizes


def get_filtered_diff_files(repo: git.Repo) -> tuple[list[str], list[str]]:
    """获取过滤后的差异文件列表"""
    all_changed_files = get_changed_files_from_status(repo)

    files_to_include: list[str] = []
    lock_files: list[str] = []

    for filename in sorted(all_changed_files):
        if filename.endswith(".lock"):
            lock_files.append(filename)
            continue

        files_to_include.append(filename)

    return files_to_include, lock_files


def _split_diff_sections(diff: str) -> list[str]:
    """Split a git diff into per-file sections."""
    if not diff:
        return []

    sections: list[str] = []
    current_section: list[str] = []

    for line in diff.splitlines(keepends=True):
        if line.startswith("diff --git ") and current_section:
            sections.append("".join(current_section))
            current_section = [line]
            continue
        current_section.append(line)

    if current_section:
        sections.append("".join(current_section))

    return sections


def _truncate_diff_section(diff_section: str) -> str:
    """Trim oversized single-file diffs while keeping the head and tail."""
    section_line_count = diff_section.count("\n")
    if section_line_count <= MAX_DIFF_LINES and len(diff_section) <= MAX_DIFF_SECTION_CHARS:
        return diff_section

    head = diff_section[:TRUNCATED_DIFF_HEAD_CHARS].rstrip("\n")
    tail = diff_section[-TRUNCATED_DIFF_TAIL_CHARS:].lstrip("\n")
    omitted_chars = len(diff_section) - len(head) - len(tail)

    if omitted_chars <= 0:
        return diff_section

    omission_notice = f"[INFO] Middle of this file diff omitted: {omitted_chars} characters omitted."
    return f"{head}\n\n{omission_notice}\n\n{tail}"


def _truncate_large_diff_sections(diff: str) -> str:
    """Truncate oversized sections in a multi-file git diff."""
    sections = _split_diff_sections(diff)
    if not sections:
        return diff
    return "".join(_truncate_diff_section(section) for section in sections)


def _resolve_api_key() -> str | None:
    """Resolve API key from settings or environment variables."""
    if settings.api_key:
        return settings.api_key

    provider = settings.provider
    if provider in PROVIDER_PRESETS:
        env_var = PROVIDER_PRESETS[provider][1]
        if env_var:
            env_key = os.getenv(env_var)
            if env_key:
                return env_key

    return None


def _resolve_base_url() -> str | None:
    """Resolve base URL from settings or provider defaults."""
    if settings.api_url:
        return settings.api_url

    provider = settings.provider
    if provider in PROVIDER_PRESETS:
        default_url = PROVIDER_PRESETS[provider][0]
        if default_url:
            return default_url

    return None


def _generate_commit_with_ai(diff: str, specified_type: str | None, current_branch: str) -> CommitData | None:
    """Use AI to generate a commit message via litellm."""
    import litellm  # noqa: PLC0415

    template_params = TemplateParams(
        types=commit_types,
        branch=current_branch,
        specified_type=specified_type,
    )

    model_name = settings.model or DEFAULT_MODEL
    litellm_model = _build_litellm_model_name(model_name)

    api_key = _resolve_api_key()
    base_url = _resolve_base_url()

    litellm_kwargs: dict[str, Any] = {}
    if api_key:
        litellm_kwargs["api_key"] = api_key
    if base_url:
        litellm_kwargs["api_base"] = base_url

    messages = [
        {"role": "system", "content": commit_prompt_template.render(**template_params.__dict__)},
        {"role": "user", "content": diff},
    ]

    # OpenAI-specific reasoning effort
    if _supports_reasoning(model_name) and settings.reasoning_effort:
        litellm_kwargs["reasoning_effort"] = settings.reasoning_effort

    with console.status("[bold green]Generating commit message...[/bold green]"):
        response = litellm.completion(
            model=litellm_model,
            messages=messages,
            response_model=CommitData,
            **litellm_kwargs,
        )

    # litellm returns the Pydantic model directly when response_model is used
    if isinstance(response, CommitData):
        return response
    # Fallback: extract from choices (litellm returns ModelResponse when response_model unsupported)
    choices = getattr(response, "choices", [])
    content = choices[0].message.content if choices else ""
    if content:
        return CommitData.model_validate_json(content)
    return None


def _get_repo_for_ai(current_dir: Path) -> git.Repo | None:
    try:
        return git.Repo(current_dir, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        print("[yellow]Not a git repository[/yellow]")
        return None


def _has_staged_changes(status_output: str) -> bool:
    """Return True when git status output contains staged changes."""
    return any(line and line[0] not in {" ", "?"} for line in status_output.splitlines())


def _get_changed_files_from_status_output(status_output: str) -> list[str]:
    """Extract changed file paths from `git status --short` output."""
    changed_files: list[str] = []

    for line in status_output.splitlines():
        if len(line) < NAME_STATUS_PARTS + 1:
            continue

        path_info = line[3:]
        if " -> " in path_info:
            old_path, new_path = path_info.split(" -> ", maxsplit=1)
            changed_files.extend([old_path, new_path])
            continue

        changed_files.append(path_info)

    return sorted(set(changed_files))


def _stage_all_changes_if_confirmed(repo: git.Repo) -> bool:
    """Prompt to stage all changes when the repository has no staged changes."""
    status_output = repo.git.status("--short", "--untracked-files=all")
    if not status_output.strip() or _has_staged_changes(status_output):
        return True

    changed_files = _get_changed_files_from_status_output(status_output)
    print("[yellow]No staged changes found, but the repository has modified files:[/yellow]")
    for filename in changed_files:
        print(f"[yellow]- {filename}[/yellow]")

    should_stage_all = click.confirm(
        "Stage all repository changes with 'git add .' and continue?",
        default=True,
    )
    if not should_stage_all:
        print("[yellow]Commit aborted. No staged changes to commit.[/yellow]")
        return False

    repo.git.add(".")
    return True


def _get_commit_choices() -> list[str]:
    """Return all supported commit type choices."""
    prefix = ["", "!"]
    return ["".join(data) for data in itertools.product(commit_types, prefix)] + ["version"]


def _get_manual_commit_command(args: CommitArgs, choices: list[str]) -> str | None:
    """Build the manual git commit command after validating the commit type."""
    messages = args.message
    commit_type = messages[0]
    if commit_type not in choices:
        print(f"Invalid type: {commit_type}")
        print(f"Valid types: {choices}")
        return None

    if len(messages) > 2:  # noqa: PLR2004
        commit_scope = messages[1]
        commit_msg = " ".join(messages[2:])
    else:
        commit_scope = None
        commit_msg = messages[1]

    use_emoji = args.emoji
    if use_emoji is False:
        use_emoji = settings.commit.emoji

    return get_commit_command(
        commit_type,
        commit_scope,
        commit_msg,
        use_emoji=use_emoji,
        is_breaking=args.breaking,
    )


def _build_diff_for_ai(repo: git.Repo) -> str | None:
    files_to_include, lock_files = get_filtered_diff_files(repo)
    if not files_to_include and not lock_files:
        print("[yellow]No files to commit, please add some files before using AI[/yellow]")
        return None

    diff = ""
    if lock_files:
        diff += f"[INFO] The following lock files were modified but are not included in the diff: {', '.join(lock_files)}\n"
    if files_to_include:
        raw_diff = repo.git.diff("--cached", "-M", "--", *files_to_include)
        diff += _truncate_large_diff_sections(raw_diff)

    if not diff:
        print("[yellow]No changes to commit, please add some changes before using AI[/yellow]")
        return None

    return diff


def _get_ai_response(diff: str, specified_type: str | None, current_branch: str) -> CommitData | None:
    try:
        resp = _generate_commit_with_ai(diff, specified_type, current_branch)
        if resp is None:
            print("[red]Failed to parse AI response[/red]")
            return None
    except Exception as e:
        print("[red]Could not connect to AI provider[/red]")
        print(e)
        return None
    return resp


def _is_warning_level(level: str) -> bool:
    return level.lower() == SENSITIVITY_LEVEL_WARNING


def _confirm_detected_secrets(secrets: list[PotentialSecret]) -> bool:
    if not secrets:
        return True
    warning_secrets = [secret for secret in secrets if _is_warning_level(secret.level)]
    error_secrets = [secret for secret in secrets if not _is_warning_level(secret.level)]
    if warning_secrets:
        print("[yellow]Detected potential sensitive key names (no values):[/yellow]")
        for secret in warning_secrets:
            print(f"[yellow]- {secret.file}: {secret.description}[/yellow]")
    if error_secrets:
        print("[red]Detected potential secrets in these files:[/red]")
        for secret in error_secrets:
            print(f"[red]- {secret.file}: {secret.description}[/red]")
        return click.confirm("Detected potential secrets. Continue with commit?", default=False)
    if warning_secrets:
        return click.confirm("Detected potential sensitive key names. Continue with commit?", default=True)
    return True


def get_ai_command(specified_type: str | None = None) -> str | None:
    repo = _get_repo_for_ai(Path.cwd())
    if repo is None:
        return None
    if not _stage_all_changes_if_confirmed(repo):
        return None

    diff = _build_diff_for_ai(repo)
    if diff is None:
        return None

    current_branch = repo.active_branch.name
    resp = _get_ai_response(diff, specified_type, current_branch)
    if resp is None:
        return None

    detected_secrets: list[PotentialSecret] = resp.secrets or []
    if not _confirm_detected_secrets(detected_secrets):
        print("[yellow]Commit aborted. Please review sensitive content.[/yellow]")
        return None

    # 如果用户指定了类型，则使用用户指定的类型，否则使用 AI 生成的类型
    commit_type = specified_type if specified_type is not None else resp.type

    return get_commit_command(
        commit_type,
        resp.scope,
        resp.msg,
        use_emoji=settings.commit.emoji,
        is_breaking=resp.is_breaking,
    )


@click.command()
@MESSAGE_ARG
@EMOJI_OPT
@BREAKING_OPT
@AI_OPT
def commit(
    *,
    message: tuple[str, ...],
    emoji: bool,
    breaking: bool,
    ai: bool,
) -> None:
    """Commit changes to the Git repository. Supports AI-generated commit messages or manual type/scope/message specification."""
    args = CommitArgs(message=list(message), emoji=emoji, breaking=breaking, ai=ai)
    handle_commit(args)


def handle_commit(args: CommitArgs) -> None:
    choices = _get_commit_choices()

    if args.ai or len(args.message) == 0:
        # 如果明确指定使用 AI
        command = get_ai_command()
        if not command:
            return
    elif len(args.message) == 1:
        # 如果只提供了一个参数（只有类型）
        commit_type = args.message[0]
        if commit_type not in choices:
            print(f"Invalid type: {commit_type}")
            print(f"Valid types: {choices}")
            return

        # 使用 AI 生成提交信息，但保留用户指定的类型
        command = get_ai_command(specified_type=commit_type)
        if not command:
            return
    else:
        command = _get_manual_commit_command(args, choices)
        if not command:
            return

        repo = _get_repo_for_ai(Path.cwd())
        if repo is None:
            return
        if not _stage_all_changes_if_confirmed(repo):
            return

    run_command(settings, command)
