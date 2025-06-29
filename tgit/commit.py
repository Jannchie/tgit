import argparse
import importlib
import importlib.resources
import itertools
from dataclasses import dataclass
from pathlib import Path

import git
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from rich import get_console, print

from tgit.settings import settings
from tgit.utils import get_commit_command, run_command, type_emojis

console = get_console()
with importlib.resources.path("tgit", "prompts") as prompt_path:
    env = Environment(loader=FileSystemLoader(prompt_path), autoescape=True)

commit_types = ["feat", "fix", "chore", "docs", "style", "refactor", "perf", "wip"]
commit_file = "commit.txt"
commit_prompt_template = env.get_template("commit.txt")

MAX_DIFF_LINES = 1000
NUMSTAT_PARTS = 3
NAME_STATUS_PARTS = 2
RENAME_STATUS_PARTS = 3


def define_commit_parser(subparsers: argparse._SubParsersAction) -> None:
    commit_type = ["feat", "fix", "chore", "docs", "style", "refactor", "perf"]
    commit_settings = settings.get("commit", {})
    types_settings = commit_settings.get("types", [])
    for data in types_settings:
        type_emojis[data.get("type")] = data.get("emoji")
        commit_type.append(data.get("type"))

    parser_commit = subparsers.add_parser("commit", help="commit changes following the conventional commit format")
    parser_commit.add_argument(
        "message",
        help="the first word should be the type, if the message is more than two parts, the second part should be the scope",
        nargs="*",
    )
    parser_commit.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    parser_commit.add_argument("-e", "--emoji", action="store_true", help="use emojis")
    parser_commit.add_argument("-b", "--breaking", action="store_true", help="breaking change")
    parser_commit.add_argument("-a", "--ai", action="store_true", help="use ai")
    parser_commit.set_defaults(func=handle_commit)


@dataclass
class CommitArgs:
    message: list[str]
    emoji: bool
    breaking: bool
    ai: bool


class CommitData(BaseModel):
    type: str
    scope: str | None
    msg: str
    is_breaking: bool


def get_changed_files_from_status(repo: git.Repo) -> set[str]:
    """获取所有变更的文件，包括重命名/移动的文件"""
    diff_name_status = repo.git.diff("--cached", "--name-status", "-M")
    all_changed_files = set()

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
    file_sizes = {}

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

    files_to_include = []
    lock_files = []

    # 过滤文件
    for filename in all_changed_files:
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


def _create_openai_client():  # type: ignore[misc]  # noqa: ANN202
    """创建并配置 OpenAI 客户端"""
    openai = _import_openai()
    client = openai.Client()
    api_url = settings.get("apiUrl")
    if api_url:
        client.base_url = api_url
    api_key = settings.get("apiKey")
    if api_key:
        client.api_key = api_key
    return client


def _generate_commit_with_ai(diff: str, specified_type: str | None, current_branch: str) -> CommitData | None:
    """使用 AI 生成提交消息"""
    _check_openai_availability()
    client = _create_openai_client()

    template_params = {"types": commit_types, "branch": current_branch}
    if specified_type:
        template_params["specified_type"] = specified_type

    with console.status("[bold green]Generating commit message...[/bold green]"):
        chat_completion = client.responses.parse(
            input=[
                {
                    "role": "system",
                    "content": commit_prompt_template.render(**template_params),
                },
                {"role": "user", "content": diff},
            ],
            model=settings.get("model", "gpt-4.1"),
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

    # 如果用户指定了类型，则使用用户指定的类型
    commit_type = specified_type or resp.type

    return get_commit_command(
        commit_type,
        resp.scope,
        resp.msg,
        use_emoji=settings.get("commit", {}).get("emoji", False),
        is_breaking=resp.is_breaking,
    )


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
            use_emoji = settings.get("commit", {}).get("emoji", False)
        is_breaking = args.breaking
        command = get_commit_command(commit_type, commit_scope, commit_msg, use_emoji=use_emoji, is_breaking=is_breaking)

    run_command(command)
