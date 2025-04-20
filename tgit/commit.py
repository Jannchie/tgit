import argparse
import importlib.resources
import itertools
from dataclasses import dataclass
from pathlib import Path

import git
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from rich import print  # noqa: A004

from tgit.settings import settings
from tgit.utils import get_commit_command, run_command, type_emojis

with importlib.resources.path("tgit", "prompts") as prompt_path:
    env = Environment(loader=FileSystemLoader(prompt_path), autoescape=True)

commit_types = ["feat", "fix", "chore", "docs", "style", "refactor", "perf", "wip"]
commit_file = "commit.txt"
commit_prompt_template = env.get_template("commit.txt")


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


def get_ai_command(specified_type: str | None = None) -> str | None:
    current_dir = Path.cwd()
    try:
        repo = git.Repo(current_dir, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        print("[yellow]Not a git repository[/yellow]")
        return None
    diff = repo.git.diff("--cached")

    current_branch = repo.active_branch.name

    if not diff:
        print("[yellow]No changes to commit, please add some changes before using AI[/yellow]")
        return None
    try:
        from litellm import completion

        # 准备模板渲染参数，如果用户指定了类型，则传递给模板
        template_params = {"types": commit_types, "branch": current_branch}

        if specified_type:
            template_params["specified_type"] = specified_type

        chat_completion = completion(
            messages=[
                {
                    "role": "system",
                    "content": commit_prompt_template.render(**template_params),
                },
                {"role": "user", "content": diff},
            ],
            model=settings.get("model", "openai/gpt-4o"),
            api_key=settings.get("apiKey", None),
            base_url=settings.get("apiUrl", None),
            max_tokens=200,
            response_format=CommitData,
        )
    except Exception:
        print("[red]Could not connect to AI provider[/red]")
        return None
    resp = CommitData.model_validate_json(chat_completion.choices[0].message.content)

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
