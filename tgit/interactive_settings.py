"""Interactive settings configuration for TGIT."""

import json
from pathlib import Path
from typing import Any

import questionary
from questionary import Choice
from rich import print

from tgit.constants import DEFAULT_MODEL, REASONING_EFFORT_CHOICES, REASONING_MODEL_HINTS
from tgit.utils import load_global_settings, load_settings, load_workspace_settings

WORKSPACE_BOOL_INHERIT = "inherit"
WORKSPACE_BOOL_TRUE = "true"
WORKSPACE_BOOL_FALSE = "false"
WORKSPACE_PROMPT_CANCEL = object()


def _get_global_settings_path() -> Path:
    """Return the global settings path."""
    return Path.home() / ".tgit" / "settings.json"


def _get_workspace_settings_path() -> Path:
    """Return the workspace settings path."""
    return Path.cwd() / ".tgit" / "settings.json"


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

    global_settings_path = _get_global_settings_path()
    workspace_settings_path = _get_workspace_settings_path()
    global_settings = load_global_settings()
    workspace_settings = load_workspace_settings()
    effective_settings = _get_effective_settings_dict()

    print(f"\n[blue]Global Settings:[/blue] {global_settings_path}")
    if global_settings:
        print(json.dumps(global_settings, indent=2, ensure_ascii=False))
    else:
        print("No global settings found")

    print(f"\n[blue]Workspace Settings:[/blue] {workspace_settings_path}")
    if workspace_settings:
        print(json.dumps(workspace_settings, indent=2, ensure_ascii=False))
    else:
        print("No workspace settings found")

    print("\n[blue]Effective Settings:[/blue]")
    print(json.dumps(effective_settings, indent=2, ensure_ascii=False))

    input("\nPress Enter to continue...")


def _configure_global_settings() -> None:  # noqa: C901, PLR0911
    """Configure global settings interactively."""
    global_settings_path = _get_global_settings_path()
    current_settings = load_global_settings()

    print(f"[blue]Target settings path:[/blue] {global_settings_path}")

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
        default=current_settings.get("model", DEFAULT_MODEL),
    ).ask()
    if model is None:
        return

    reasoning_effort = questionary.text(
        "Reasoning effort (leave empty for automatic)",
        default=current_settings.get("reasoning_effort", ""),
        validate=_validate_reasoning_effort,
    ).ask()
    if reasoning_effort is None:
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
        "reasoning_effort": _normalize_reasoning_effort(reasoning_effort),
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
    if not new_settings["reasoning_effort"]:
        del new_settings["reasoning_effort"]
    if not new_settings["commit"]["types"]:
        del new_settings["commit"]["types"]

    # Save to global settings
    global_settings_path.parent.mkdir(parents=True, exist_ok=True)
    global_settings_path.write_text(json.dumps(new_settings, indent=2, ensure_ascii=False))

    print(f"[green]Global settings saved successfully:[/green] {global_settings_path}")


def _configure_workspace_settings() -> None:  # noqa: C901, PLR0911, PLR0912
    """Configure workspace-specific settings."""
    workspace_settings_path = _get_workspace_settings_path()
    global_settings = load_global_settings()
    current_settings = load_workspace_settings()
    effective_settings = _get_effective_settings_dict()

    print(f"[blue]Target settings path:[/blue] {workspace_settings_path}")

    if not questionary.confirm(
        f"Configure workspace settings in {workspace_settings_path}?",
        default=True,
    ).ask():
        return

    # Collect all inputs with early returns on cancel
    api_key = questionary.text(
        "OpenAI API Key (leave empty to inherit from global)",
        default=effective_settings.get("apiKey", ""),
    ).ask()
    if api_key is None:
        return

    api_url = questionary.text(
        "API URL (leave empty to inherit from global)",
        default=effective_settings.get("apiUrl", ""),
    ).ask()
    if api_url is None:
        return

    model = questionary.text(
        "Model name (leave empty to inherit from global/default)",
        default=effective_settings.get("model", DEFAULT_MODEL),
    ).ask()
    if model is None:
        return

    reasoning_effort = questionary.text(
        "Reasoning effort (leave empty to inherit/auto)",
        default=effective_settings.get("reasoning_effort", ""),
        validate=_validate_reasoning_effort,
    ).ask()
    if reasoning_effort is None:
        return

    show_command = _prompt_workspace_bool_setting(
        "Show git commands before execution",
        current_override=current_settings.get("show_command") if "show_command" in current_settings else None,
        inherited_value=global_settings.get("show_command", True),
    )
    if show_command is WORKSPACE_PROMPT_CANCEL:
        return

    skip_confirm = _prompt_workspace_bool_setting(
        "Skip confirmation prompts",
        current_override=current_settings.get("skip_confirm") if "skip_confirm" in current_settings else None,
        inherited_value=global_settings.get("skip_confirm", False),
    )
    if skip_confirm is WORKSPACE_PROMPT_CANCEL:
        return

    commit_emoji = _prompt_workspace_bool_setting(
        "Use emoji in commit messages",
        current_override=current_settings.get("commit", {}).get("emoji") if "emoji" in current_settings.get("commit", {}) else None,
        inherited_value=global_settings.get("commit", {}).get("emoji", False),
    )
    if commit_emoji is WORKSPACE_PROMPT_CANCEL:
        return

    inherited_api_key = global_settings.get("apiKey", "")
    inherited_api_url = global_settings.get("apiUrl", "")
    inherited_model = global_settings.get("model", DEFAULT_MODEL)
    inherited_reasoning_effort = _resolve_reasoning_effort_for_display(
        inherited_model,
        global_settings.get("reasoning_effort", ""),
    )
    inherited_show_command = global_settings.get("show_command", True)
    inherited_skip_confirm = global_settings.get("skip_confirm", False)
    inherited_commit_emoji = global_settings.get("commit", {}).get("emoji", False)

    new_settings: dict[str, Any] = {}

    if api_key and api_key != inherited_api_key:
        new_settings["apiKey"] = api_key
    if api_url and api_url != inherited_api_url:
        new_settings["apiUrl"] = api_url
    if model and model != inherited_model:
        new_settings["model"] = model
    normalized_reasoning_effort = _normalize_reasoning_effort(reasoning_effort)
    if normalized_reasoning_effort and normalized_reasoning_effort != inherited_reasoning_effort:
        new_settings["reasoning_effort"] = normalized_reasoning_effort
    if show_command is not None and show_command != inherited_show_command:
        new_settings["show_command"] = show_command
    if skip_confirm is not None and skip_confirm != inherited_skip_confirm:
        new_settings["skip_confirm"] = skip_confirm
    if commit_emoji is not None and commit_emoji != inherited_commit_emoji:
        new_settings["commit"] = {"emoji": commit_emoji}

    # Save to workspace settings
    workspace_settings_path.parent.mkdir(parents=True, exist_ok=True)
    workspace_settings_path.write_text(json.dumps(new_settings, indent=2, ensure_ascii=False))

    print(f"[green]Workspace settings saved successfully:[/green] {workspace_settings_path}")


def _get_effective_settings_dict() -> dict[str, Any]:
    """Return effective settings with defaults applied for display and prompts."""
    effective_settings = load_settings()

    commit_settings: dict[str, Any] = {
        "emoji": effective_settings.commit.emoji,
    }
    if effective_settings.commit.types:
        commit_settings["types"] = [
            {"type": commit_type.type, "emoji": commit_type.emoji}
            for commit_type in effective_settings.commit.types
        ]

    return {
        "apiKey": effective_settings.api_key,
        "apiUrl": effective_settings.api_url,
        "model": effective_settings.model,
        "reasoning_effort": _resolve_reasoning_effort_for_display(
            effective_settings.model,
            effective_settings.reasoning_effort,
        ),
        "show_command": effective_settings.show_command,
        "skip_confirm": effective_settings.skip_confirm,
        "commit": commit_settings,
    }


def _prompt_workspace_bool_setting(prompt: str, *, current_override: bool | None, inherited_value: bool) -> bool | None | object:
    """Prompt for a workspace boolean override using follow/true/false choices."""
    current_label = "enabled" if inherited_value else "disabled"
    default_choice = WORKSPACE_BOOL_INHERIT
    if current_override is not None:
        default_choice = WORKSPACE_BOOL_TRUE if current_override else WORKSPACE_BOOL_FALSE

    choice = questionary.select(
        prompt,
        choices=[
            Choice(title=f"Follow global/default (current: {current_label})", value=WORKSPACE_BOOL_INHERIT),
            Choice(title="Enabled", value=WORKSPACE_BOOL_TRUE),
            Choice(title="Disabled", value=WORKSPACE_BOOL_FALSE),
        ],
        default=default_choice,
    ).ask()

    if choice is None:
        return WORKSPACE_PROMPT_CANCEL
    if choice == WORKSPACE_BOOL_INHERIT:
        return None
    return choice == WORKSPACE_BOOL_TRUE


def _validate_reasoning_effort(value: str) -> bool | str:
    """Validate a reasoning effort override."""
    normalized_value = _normalize_reasoning_effort(value)
    if not normalized_value or normalized_value in REASONING_EFFORT_CHOICES:
        return True
    return "Use empty/auto/default or one of: " + ", ".join(REASONING_EFFORT_CHOICES)


def _normalize_reasoning_effort(value: str) -> str:
    """Normalize a reasoning effort override for storage."""
    normalized_value = value.strip().lower()
    if normalized_value in {"", "auto", "default"}:
        return ""
    return normalized_value


def _supports_reasoning_model(model: str) -> bool:
    """Return True when the selected model supports reasoning parameters."""
    if not model:
        return False
    model_lower = model.lower()
    return any(hint in model_lower for hint in REASONING_MODEL_HINTS)


def _get_default_reasoning_effort(model: str) -> str:
    """Return the default reasoning effort for a reasoning-capable model."""
    model_lower = model.lower()

    if model_lower.startswith("gpt-5.4") and not model_lower.startswith("gpt-5.4-pro"):
        return "none"
    if model_lower.startswith("gpt-5.1"):
        return "none"
    if model_lower.startswith("gpt-5"):
        return "medium"
    return ""


def _resolve_reasoning_effort_for_display(model: str, configured_effort: str) -> str:
    """Resolve the effective reasoning effort for prompts and view output."""
    normalized_effort = _normalize_reasoning_effort(configured_effort)
    if normalized_effort:
        return normalized_effort
    if _supports_reasoning_model(model):
        return _get_default_reasoning_effort(model)
    return ""


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
        global_settings_path = _get_global_settings_path()
        if global_settings_path.exists():
            global_settings_path.unlink()
            print("[green]Global settings reset successfully![/green]")
        else:
            print("[yellow]Global settings file does not exist.[/yellow]")

    if reset_type in ["workspace", "both"]:
        workspace_settings_path = _get_workspace_settings_path()
        if workspace_settings_path.exists():
            workspace_settings_path.unlink()
            print("[green]Workspace settings reset successfully![/green]")
        else:
            print("[yellow]Workspace settings file does not exist.[/yellow]")
