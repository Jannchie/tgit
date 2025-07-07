import click
from rich import print

from tgit.utils import set_global_settings


@click.command()
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.option("--interactive", "-i", is_flag=True, help="Interactive configuration mode")
def settings_command(
    key: str | None,
    value: str | None,
    *,
    interactive: bool,
) -> None:
    """Configure TGIT settings interactively or via key-value pairs."""
    if interactive or (key is None and value is None):
        from tgit.interactive_settings import interactive_settings  # noqa: PLC0415

        interactive_settings()
        return

    if not key or not value:
        print("Both key and value are required when not using interactive mode")
        print("Use --interactive or -i for interactive configuration")
        raise click.Abort

    available_keys = ["apiKey", "apiUrl", "model", "show_command", "skip_confirm"]

    if key not in available_keys:
        print(f"Key {key} is not valid. Available keys: {', '.join(available_keys)}")
        raise click.Abort
    true_value = value
    # Convert boolean strings
    if key in ["show_command", "skip_confirm"]:
        if value.lower() in ["true", "1", "yes", "on"]:
            true_value = True
        elif value.lower() in ["false", "0", "no", "off"]:
            true_value = False
        else:
            print(f"Invalid boolean value for {key}. Use true/false, 1/0, yes/no, or on/off")
            raise click.Abort

    set_global_settings(key, true_value)
    print(f"[green]Setting {key} updated successfully![/green]")
