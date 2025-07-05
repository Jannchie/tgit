import typer

from tgit.utils import simple_run_command


def add(
    files: list[str] = typer.Argument(..., help="files to add"),
) -> None:
    files_str = " ".join(files)
    command = f"git add {files_str}"
    simple_run_command(command)
