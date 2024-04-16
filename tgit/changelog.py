from dataclasses import dataclass

from tgit.utils import console


def define_changelog_parser(subparsers):
    parser_changelog = subparsers.add_parser("changelog", help="generate changelogs")
    parser_changelog.add_argument("-f", "--from", help="From hash/tag", type=str, dest="from_raw")
    parser_changelog.add_argument("-t", "--to", help="To hash/tag", type=str, dest="to_raw")
    parser_changelog.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    parser_changelog.set_defaults(func=handle_changelog)


@dataclass
class ChangelogArgs:
    from_raw: str
    to_raw: str


def handle_changelog(args: ChangelogArgs):
    from_raw = args.from_raw
    to_raw = args.to_raw
    console.log(f"{from_raw} -> {to_raw}")
    console.log(args)
    console.log("WIP")
