from tgit.utils import simple_run_command


def define_add_parser(subparsers):
    parser_add = subparsers.add_parser("add", help="same as git add")
    parser_add.add_argument("files", help="files to add", nargs="*")
    parser_add.set_defaults(func=handle_add)


def handle_add(args):
    files = " ".join(args.files)
    command = f"git add {files}"
    simple_run_command(command)
