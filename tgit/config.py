import click
from rich import print

from .interactive_settings import interactive_settings
from .settings import set_global_settings


@click.command()
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.option("--interactive", "-i", is_flag=True, help="Interactive configuration mode")
def config(
    key: str | None,
    value: str | None,
    interactive: bool,
) -> None:
    if interactive or (key is None and value is None):
        interactive_settings()
        return

    if key is None or value is None:
        print("Both key and value are required when not using interactive mode")
        print("Use --interactive or -i for interactive configuration")
        raise click.Abort

    available_keys = ["apiKey", "apiUrl", "model", "show_command", "skip_confirm"]

    if key not in available_keys:
        print(f"Key {key} is not valid. Available keys: {', '.join(available_keys)}")
        raise click.Abort

    # Convert boolean strings
    if key in ["show_command", "skip_confirm"]:
        if value.lower() in ["true", "1", "yes", "on"]:
            value = True
        elif value.lower() in ["false", "0", "no", "off"]:
            value = False
        else:
            print(f"Invalid boolean value for {key}. Use true/false, 1/0, yes/no, or on/off")
            raise click.Abort

    set_global_settings(key, value)
    print(f"[green]Setting {key} updated successfully![/green]")
