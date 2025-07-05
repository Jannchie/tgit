import typer

from tgit.utils import simple_run_command

# Define typer arguments/options at module level to avoid B008
FILES_ARG = typer.Argument(..., help="files to add")


def add(
    files: list[str] = FILES_ARG,
) -> None:
    files_str = " ".join(files)
    command = f"git add {files_str}"
    simple_run_command(command)
