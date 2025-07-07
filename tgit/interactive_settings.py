"""Interactive settings configuration for TGIT."""

import json
from pathlib import Path
from typing import Any

import questionary
from questionary import Choice
from rich import print

from tgit.utils import load_global_settings, load_workspace_settings


def interactive_settings() -> None:
    """Interactive settings configuration."""
    print("[bold blue]TGIT Interactive Settings[/bold blue]")
    print("Configure your TGIT settings interactively.")

    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=[
                Choice(title="View current settings", value="view"),
                Choice(title="Configure global settings", value="global"),
                Choice(title="Configure workspace settings", value="workspace"),
                Choice(title="Reset settings", value="reset"),
                Choice(title="Exit", value="exit"),
            ],
        ).ask()

        if not action or action == "exit":
            break

        if action == "view":
            _view_current_settings()
        elif action == "global":
            _configure_global_settings()
        elif action == "workspace":
            _configure_workspace_settings()
        elif action == "reset":
            _reset_settings()


def _view_current_settings() -> None:
    """Display current settings."""
    print("\n[bold green]Current Settings:[/bold green]")

    global_settings = load_global_settings()
    workspace_settings = load_workspace_settings()

    print("\n[blue]Global Settings:[/blue]")
    if global_settings:
        print(json.dumps(global_settings, indent=2, ensure_ascii=False))
    else:
        print("No global settings found")

    print("\n[blue]Workspace Settings:[/blue]")
    if workspace_settings:
        print(json.dumps(workspace_settings, indent=2, ensure_ascii=False))
    else:
        print("No workspace settings found")

    input("\nPress Enter to continue...")


def _configure_global_settings() -> None:
    """Configure global settings interactively."""
    current_settings = load_global_settings()

    # API Configuration
    api_key = questionary.text(
        "OpenAI API Key",
        default=current_settings.get("apiKey", ""),
    ).ask()
    if api_key is None:
        return

    api_url = questionary.text(
        "API URL (leave empty for default)",
        default=current_settings.get("apiUrl", ""),
    ).ask()
    if api_url is None:
        return

    model = questionary.text(
        "Model name",
        default=current_settings.get("model", "gpt-4o-mini"),
    ).ask()
    if model is None:
        return

    # General Configuration
    show_command = questionary.confirm(
        "Show git commands before execution",
        default=current_settings.get("show_command", True),
    ).ask()
    if show_command is None:
        return

    skip_confirm = questionary.confirm(
        "Skip confirmation prompts",
        default=current_settings.get("skip_confirm", False),
    ).ask()
    if skip_confirm is None:
        return

    commit_emoji = questionary.confirm(
        "Use emoji in commit messages",
        default=current_settings.get("commit", {}).get("emoji", False),
    ).ask()
    if commit_emoji is None:
        return

    # Commit Types Configuration
    configure_commit_types = questionary.confirm(
        "Do you want to configure custom commit types?",
        default=False,
    ).ask()
    commit_types = []

    if configure_commit_types:
        commit_types = _configure_commit_types(current_settings.get("commit", {}).get("types", []))

    # Save settings
    new_settings = {
        "apiKey": api_key,
        "apiUrl": api_url,
        "model": model,
        "show_command": show_command,
        "skip_confirm": skip_confirm,
        "commit": {
            "emoji": commit_emoji,
            "types": commit_types,
        },
    }

    # Remove empty values
    if not new_settings["apiUrl"]:
        del new_settings["apiUrl"]
    if not new_settings["commit"]["types"]:
        del new_settings["commit"]["types"]

    # Save to global settings
    global_settings_path = Path.home() / ".tgit" / "settings.json"
    global_settings_path.parent.mkdir(parents=True, exist_ok=True)
    global_settings_path.write_text(json.dumps(new_settings, indent=2, ensure_ascii=False))

    print("[green]Global settings saved successfully![/green]")


def _configure_workspace_settings() -> None:  # noqa: C901, PLR0911
    """Configure workspace-specific settings."""
    workspace_settings_path = Path.cwd() / ".tgit" / "settings.json"
    current_settings = load_workspace_settings()

    if not questionary.confirm(
        f"Configure workspace settings in {workspace_settings_path}?",
        default=True,
    ).ask():
        return

    # Collect all inputs with early returns on cancel
    api_key = questionary.text(
        "OpenAI API Key (workspace override)",
        default=current_settings.get("apiKey", ""),
    ).ask()
    if api_key is None:
        return

    api_url = questionary.text(
        "API URL (workspace override)",
        default=current_settings.get("apiUrl", ""),
    ).ask()
    if api_url is None:
        return

    model = questionary.text(
        "Model name (workspace override)",
        default=current_settings.get("model", ""),
    ).ask()
    if model is None:
        return

    show_command = questionary.confirm(
        "Show git commands before execution",
        default=current_settings.get("show_command", True),
    ).ask()
    if show_command is None:
        return

    skip_confirm = questionary.confirm(
        "Skip confirmation prompts",
        default=current_settings.get("skip_confirm", False),
    ).ask()
    if skip_confirm is None:
        return

    commit_emoji = questionary.confirm(
        "Use emoji in commit messages",
        default=current_settings.get("commit", {}).get("emoji", False),
    ).ask()
    if commit_emoji is None:
        return

    # Build settings dictionary
    new_settings = {
        "show_command": show_command,
        "skip_confirm": skip_confirm,
        "commit": {"emoji": commit_emoji},
    }

    # Add API settings if provided
    if api_key:
        new_settings["apiKey"] = api_key
    if api_url:
        new_settings["apiUrl"] = api_url
    if model:
        new_settings["model"] = model

    # Save to workspace settings
    workspace_settings_path.parent.mkdir(parents=True, exist_ok=True)
    workspace_settings_path.write_text(json.dumps(new_settings, indent=2, ensure_ascii=False))

    print(f"[green]Workspace settings saved to {workspace_settings_path}![/green]")


def _configure_commit_types(_: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Configure custom commit types."""
    commit_types = []

    default_types = [
        {"type": "feat", "emoji": "✨"},
        {"type": "fix", "emoji": "🐛"},
        {"type": "docs", "emoji": "📚"},
        {"type": "style", "emoji": "💎"},
        {"type": "refactor", "emoji": "📦"},
        {"type": "perf", "emoji": "🚀"},
        {"type": "test", "emoji": "🚨"},
        {"type": "chore", "emoji": "♻️"},
        {"type": "ci", "emoji": "🎡"},
        {"type": "version", "emoji": "🔖"},
    ]

    print("\n[blue]Configure Commit Types:[/blue]")
    print("Configure custom commit types and their emojis.")

    use_defaults = questionary.confirm(
        "Use default commit types?",
        default=True,
    ).ask()
    if use_defaults:
        return default_types

    # Custom commit types configuration
    while True:
        commit_type = questionary.text(
            "Commit type (e.g., feat, fix, docs)",
            validate=lambda x: len(x.strip()) > 0 or "Please enter a valid commit type",
        ).ask()
        if not commit_type:
            break

        emoji = questionary.text(
            "Emoji for this type",
            default="✨",
        ).ask()
        if not emoji:
            break

        commit_types.append(
            {
                "type": commit_type.strip(),
                "emoji": emoji.strip(),
            },
        )

        continue_adding = questionary.confirm(
            "Add another commit type?",
            default=False,
        ).ask()
        if not continue_adding:
            break

    return commit_types


def _reset_settings() -> None:
    """Reset settings to default."""
    reset_type = questionary.select(
        "What would you like to reset?",
        choices=[
            Choice(title="Global settings", value="global"),
            Choice(title="Workspace settings", value="workspace"),
            Choice(title="Both", value="both"),
            Choice(title="Cancel", value="cancel"),
        ],
    ).ask()
    if not reset_type or reset_type == "cancel":
        return

    confirm = questionary.confirm(
        "Are you sure you want to reset the settings? This cannot be undone.",
        default=False,
    ).ask()
    if not confirm:
        print("[yellow]Reset cancelled.[/yellow]")
        return

    if reset_type in ["global", "both"]:
        global_settings_path = Path.home() / ".tgit" / "settings.json"
        if global_settings_path.exists():
            global_settings_path.unlink()
            print("[green]Global settings reset successfully![/green]")
        else:
            print("[yellow]Global settings file does not exist.[/yellow]")

    if reset_type in ["workspace", "both"]:
        workspace_settings_path = Path.cwd() / ".tgit" / "settings.json"
        if workspace_settings_path.exists():
            workspace_settings_path.unlink()
            print("[green]Workspace settings reset successfully![/green]")
        else:
            print("[yellow]Workspace settings file does not exist.[/yellow]")
