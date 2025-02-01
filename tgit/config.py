import argparse

from rich import print  # noqa: A004

from .settings import set_global_settings


def define_config_parser(subparsers: argparse._SubParsersAction) -> None:
    # edit api key / edit api url
    parser_config = subparsers.add_parser("config", help="edit settings")
    parser_config.add_argument("key", help="setting key")
    parser_config.add_argument("value", help="setting value")
    parser_config.set_defaults(func=handle_config)


def handle_config(args: argparse.Namespace) -> int:
    if not args.key:
        print("Key is required")
        return 1
    if not args.value:
        print("Value is required")
        return 1

    avaliable_keys = ["apiKey", "apiUrl", "model"]

    if args.key not in avaliable_keys:
        print(f"Key {args.key} is not valid")
        return 1
    set_global_settings(args.key, args.value)
    return 0
