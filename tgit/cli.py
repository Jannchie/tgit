import contextlib
import importlib.metadata
import threading

import click

from tgit.add import add
from tgit.changelog import changelog
from tgit.commit import commit
from tgit.settings import settings_command
from tgit.utils import console
from tgit.version import version


def version_callback(ctx: click.Context, _param: click.Parameter, value: bool) -> None:  # noqa: FBT001
    if not value or ctx.resilient_parsing:
        return
    version_info = importlib.metadata.version("tgit")
    console.print(f"TGIT - ver.{version_info}", highlight=False)
    ctx.exit()


@click.group(
    name="tgit",
    help="TGIT cli",
    no_args_is_help=True,
)
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=version_callback,
    help="Show version",
)
def app() -> None:
    def import_openai() -> None:
        with contextlib.suppress(Exception):
            import openai  # noqa: F401, PLC0415

    threading.Thread(target=import_openai).start()


# Add individual commands directly to the main app
app.add_command(commit)
app.add_command(version)
app.add_command(changelog)
app.add_command(add)
app.add_command(settings_command, name="settings")


if __name__ == "__main__":
    app()
