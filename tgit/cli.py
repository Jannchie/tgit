import argparse
import importlib.metadata

import rich
import rich.traceback

from tgit.changelog import define_changelog_parser
from tgit.commit import define_commit_parser
from tgit.utils import console
from tgit.version import define_version_parser

rich.traceback.install()


def main():
    parser = argparse.ArgumentParser(
        description="TGIT cli",
        prog="tgit",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--version", action="store_true", help="show version")
    subparsers = parser.add_subparsers(title="Subcommands")

    define_commit_parser(subparsers)
    define_version_parser(subparsers)
    define_changelog_parser(subparsers)

    args = parser.parse_args()
    handle(parser, args)


def handle(parser, args):
    if hasattr(args, "func"):
        args.func(args)
    elif args.version:
        version = importlib.metadata.version("tgit")
        console.print(f"TGIT - ver.{version}", highlight=False)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
