import click

from tgit.utils import simple_run_command

# Define click arguments/options at module level to avoid B008
FILES_ARG = click.argument("files", nargs=-1, required=True)


@click.command()
@FILES_ARG
def add(
    files: tuple[str, ...],
) -> None:
    """Add specified files to the git staging area."""
    files_str = " ".join(files)
    command = f"git add {files_str}"
    simple_run_command(command)
