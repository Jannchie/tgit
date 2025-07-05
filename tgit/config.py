import typer
from rich import print

from .settings import set_global_settings


def config(
    key: str = typer.Argument(..., help="setting key"),
    value: str = typer.Argument(..., help="setting value"),
) -> None:
    available_keys = ["apiKey", "apiUrl", "model"]

    if key not in available_keys:
        print(f"Key {key} is not valid")
        raise typer.Exit(1)

    set_global_settings(key, value)
