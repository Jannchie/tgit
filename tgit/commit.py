import itertools
from dataclasses import dataclass
from typing import Optional

from tgit.settings import settings
from tgit.utils import get_commit_command, run_command, type_emojis


def define_commit_parser(subparsers):
    commit_type = ["feat", "fix", "chore", "docs", "style", "refactor", "perf"]
    prefix = ["!", ""]
    commit_settings = settings.get("commit", {})
    types_settings = commit_settings.get("types", [])
    for data in types_settings:
        type_emojis[data.get("type")] = data.get("emoji")
        commit_type.append(data.get("type"))

    choices = ["".join(data) for data in itertools.product(commit_type, prefix)] + ["ci", "test", "version"]
    parser_commit = subparsers.add_parser("commit", help="commit changes following the conventional commit format")
    parser_commit.add_argument(
        "type",
        help="commit type",
        choices=choices,
    )
    parser_commit.add_argument("scope", help="commit scope", type=str, nargs="?")
    parser_commit.add_argument("message", help="commit message", type=str)
    parser_commit.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    parser_commit.add_argument("-e", "--emoji", action="store_true", help="use emojis")
    parser_commit.add_argument("-b", "--breaking", action="store_true", help="breaking change")
    parser_commit.set_defaults(func=handle_commit)


@dataclass
class CommitArgs:
    type: str
    scope: Optional[str]
    message: str
    emoji: bool
    breaking: bool


def handle_commit(args: CommitArgs):

    commit_type = args.type
    commit_scope = args.scope
    commit_msg = args.message
    use_emojis = args.emoji
    is_breaking = args.breaking
    command = get_commit_command(commit_type, commit_scope, commit_msg, use_emojis, is_breaking)
    run_command(command)
