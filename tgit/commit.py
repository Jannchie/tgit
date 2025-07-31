import importlib
import importlib.resources
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import click
import git
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from rich import get_console, print

from tgit.shared import settings
from tgit.utils import get_commit_command, run_command, type_emojis

if TYPE_CHECKING:
    from openai import Client

console = get_console()
with importlib.resources.path("tgit", "prompts") as prompt_path:
    env = Environment(loader=FileSystemLoader(prompt_path), autoescape=True)

commit_types = ["feat", "fix", "chore", "docs", "style", "refactor", "perf", "wip"]
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
NUMSTAT_PARTS = 3
NAME_STATUS_PARTS = 2
RENAME_STATUS_PARTS = 3


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


class CommitData(BaseModel):
    type: str
    scope: str | None
    msg: str
    is_breaking: bool


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
    file_sizes = get_file_change_sizes(repo)

    files_to_include: list[str] = []
    lock_files: list[str] = []

    # 过滤文件
    for filename in sorted(all_changed_files):
        if filename.endswith(".lock"):
            lock_files.append(filename)
            continue

        # 检查文件大小（如果有统计信息）
        total_changes = file_sizes.get(filename, 0)
        if total_changes <= MAX_DIFF_LINES:
            files_to_include.append(filename)

    return files_to_include, lock_files


def _import_openai():  # type: ignore[misc]  # noqa: ANN202
    """动态导入 openai 包"""
    try:
        # 动态导入，避免在模块级别导入
        return importlib.import_module("openai")
    except ImportError as e:
        error_msg = "openai package is not installed"
        raise ImportError(error_msg) from e


def _check_openai_availability() -> None:
    """检查 openai 包是否可用"""
    _import_openai()  # 这会在包不可用时抛出异常


def _create_openai_client() -> "Client":  # type: ignore[misc]
    """创建并配置 OpenAI 客户端"""
    openai = _import_openai()

    # 准备客户端参数
    kwargs = {}
    if settings.api_key:
        kwargs["api_key"] = settings.api_key
    if settings.api_url:
        kwargs["base_url"] = settings.api_url

    return openai.Client(**kwargs)


def _generate_commit_with_ai(diff: str, specified_type: str | None, current_branch: str) -> CommitData | None:
    """使用 AI 生成提交消息"""
    _check_openai_availability()
    client = _create_openai_client()

    template_params = TemplateParams(
        types=commit_types,
        branch=current_branch,
        specified_type=specified_type,
    )

    with console.status("[bold green]Generating commit message...[/bold green]"):
        chat_completion = client.responses.parse(
            input=[
                {
                    "role": "system",
                    "content": commit_prompt_template.render(**template_params.__dict__),
                },
                {"role": "user", "content": diff},
            ],
            model=settings.model or "gpt-4.1",
            max_output_tokens=50,
            text_format=CommitData,
        )

    return chat_completion.output_parsed


def get_ai_command(specified_type: str | None = None) -> str | None:
    current_dir = Path.cwd()
    try:
        repo = git.Repo(current_dir, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        print("[yellow]Not a git repository[/yellow]")
        return None

    files_to_include, lock_files = get_filtered_diff_files(repo)
    if not files_to_include and not lock_files:
        print("[yellow]No files to commit, please add some files before using AI[/yellow]")
        return None

    diff = ""
    if lock_files:
        diff += f"[INFO] The following lock files were modified but are not included in the diff: {', '.join(lock_files)}\n"
    if files_to_include:
        diff += repo.git.diff("--cached", "-M", "--", *files_to_include)
    current_branch = repo.active_branch.name

    if not diff:
        print("[yellow]No changes to commit, please add some changes before using AI[/yellow]")
        return None

    try:
        resp = _generate_commit_with_ai(diff, specified_type, current_branch)
        if resp is None:
            print("[red]Failed to parse AI response[/red]")
            return None
    except Exception as e:
        print("[red]Could not connect to AI provider[/red]")
        print(e)
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
    prefix = ["", "!"]
    choices = ["".join(data) for data in itertools.product(commit_types, prefix)] + ["ci", "test", "version"]

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
        # 正常的提交流程
        messages = args.message
        commit_type = messages[0]
        if len(messages) > 2:  # noqa: PLR2004
            commit_scope = messages[1]
            commit_msg = " ".join(messages[2:])
        else:
            commit_scope = None
            commit_msg = messages[1]
        if commit_type not in choices:
            print(f"Invalid type: {commit_type}")
            print(f"Valid types: {choices}")
            return
        use_emoji = args.emoji
        if use_emoji is False:
            use_emoji = settings.commit.emoji
        is_breaking = args.breaking
        command = get_commit_command(commit_type, commit_scope, commit_msg, use_emoji=use_emoji, is_breaking=is_breaking)

    run_command(settings, command)
