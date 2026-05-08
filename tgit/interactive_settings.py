"""Interactive settings configuration for TGIT."""

import json
from pathlib import Path
from typing import Any

import questionary
from questionary import Choice
from rich.console import Console

from tgit.constants import DEFAULT_MODEL, OPENAI_REASONING_MODEL_HINTS, PROVIDER_PRESETS, REASONING_EFFORT_CHOICES
from tgit.utils import load_global_settings, load_settings, load_workspace_settings

console = Console()

WORKSPACE_BOOL_INHERIT = "inherit"
WORKSPACE_BOOL_TRUE = "true"
WORKSPACE_BOOL_FALSE = "false"
WORKSPACE_PROMPT_CANCEL = object()
MASK_THRESHOLD = 8


def _get_global_settings_path() -> Path:
    """Return the global settings path."""
    return Path.home() / ".tgit" / "settings.json"


def _get_workspace_settings_path() -> Path:
    """Return the workspace settings path."""
    return Path.cwd() / ".tgit" / "settings.json"


def interactive_settings() -> None:
    """Interactive settings configuration."""
    console.print("[bold]TGIT Interactive Settings[/bold]")
    console.print("Configure your TGIT settings interactively.")

    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=[
                Choice(title="Configure global settings", value="global"),
                Choice(title="Configure workspace settings", value="workspace"),
                Choice(title="Reset settings", value="reset"),
                Choice(title="Exit", value="exit"),
            ],
        ).ask()

        if not action or action == "exit":
            break

        if action == "global":
            _configure_global_settings()
        elif action == "workspace":
            _configure_workspace_settings()
        elif action == "reset":
            _reset_settings()


def _mask_key(key: str) -> str:
    """Return a masked version of an API key for display."""
    if not key:
        return "(not set)"
    if len(key) <= MASK_THRESHOLD:
        return "****"
    return key[:4] + "****" + key[-4:]


def _configure_global_settings() -> None:  # noqa: C901, PLR0912, PLR0915
    """Configure global settings via a table-based editor."""
    global_settings_path = _get_global_settings_path()
    current = load_global_settings()

    console.print(f"\nTarget: {global_settings_path}")

    while True:
        provider = current.get("provider", "auto")
        api_key = current.get("apiKey", "")
        api_url = current.get("apiUrl", "")
        model = current.get("model", "") or PROVIDER_PRESETS.get(provider, ("", "", DEFAULT_MODEL))[2]
        reasoning_effort = current.get("reasoning_effort", "")
        show_command = current.get("show_command", True)
        skip_confirm = current.get("skip_confirm", False)
        commit_emoji = current.get("commit", {}).get("emoji", False)
        commit_types = current.get("commit", {}).get("types", [])

        choice = questionary.select(
            "Select a setting to edit:",
            choices=[
                Choice(title=[("class:ansicyan", f"{'Provider':18s}"), ("", f" → {provider}")], value="provider"),
                Choice(title=[("class:ansicyan", f"{'API Key':18s}"), ("", f" → {_mask_key(api_key)}")], value="apiKey"),
                Choice(title=[("class:ansicyan", f"{'API URL':18s}"), ("", f" → {api_url or '(default)'}")], value="apiUrl"),
                Choice(title=[("class:ansicyan", f"{'Model':18s}"), ("", f" → {model}")], value="model"),
                Choice(
                    title=[("class:ansicyan", f"{'Reasoning Effort':18s}"), ("", f" → {reasoning_effort or '(auto)'}")],
                    value="reasoning_effort",
                ),
                Choice(
                    title=[("class:ansicyan", f"{'Show Command':18s}"), ("", f" → {'Yes' if show_command else 'No'}")], value="show_command"
                ),
                Choice(
                    title=[("class:ansicyan", f"{'Skip Confirm':18s}"), ("", f" → {'Yes' if skip_confirm else 'No'}")], value="skip_confirm"
                ),
                Choice(
                    title=[("class:ansicyan", f"{'Use Emoji':18s}"), ("", f" → {'Yes' if commit_emoji else 'No'}")], value="commit_emoji"
                ),
                Choice(
                    title=[
                        ("class:ansicyan", f"{'Commit Types':18s}"),
                        ("", f" → {'defaults' if not commit_types else f'{len(commit_types)} custom types'}"),
                    ],
                    value="commit_types",
                ),
                Choice(title="─" * 50, disabled="—"),
                Choice(title="Exit", value="exit"),
            ],
        ).ask()

        if choice is None:
            return

        if choice == "exit":
            break

        if choice == "provider":
            new_provider = questionary.select(
                "LLM Provider",
                choices=[Choice(title=f"{p}  (default model: {info[2]})", value=p) for p, info in PROVIDER_PRESETS.items()],
                default=provider,
            ).ask()
            if new_provider is not None:
                current["provider"] = new_provider
                if "model" not in current:
                    current["model"] = PROVIDER_PRESETS[new_provider][2]

        elif choice == "apiKey":
            label = "API Key"
            if provider in PROVIDER_PRESETS and PROVIDER_PRESETS[provider][1]:
                label = f"API Key  (env: {PROVIDER_PRESETS[provider][1]})"
            if api_key:
                label += f"  (current: {_mask_key(api_key)}, leave empty to keep)"
            new_val = questionary.text(label, default="").ask()
            if new_val is not None and new_val:
                current["apiKey"] = new_val

        elif choice == "apiUrl":
            new_val = questionary.text(
                "API URL  (leave empty for default)",
                default=api_url,
            ).ask()
            if new_val is not None:
                if new_val:
                    current["apiUrl"] = new_val
                else:
                    current.pop("apiUrl", None)

        elif choice == "model":
            new_val = questionary.text(
                "Model name",
                default=model,
            ).ask()
            if new_val is not None and new_val:
                current["model"] = new_val

        elif choice == "reasoning_effort":
            new_val = questionary.text(
                f"Reasoning effort  ({', '.join(REASONING_EFFORT_CHOICES)})",
                default=reasoning_effort,
                validate=_validate_reasoning_effort,
            ).ask()
            if new_val is not None:
                normalized = _normalize_reasoning_effort(new_val)
                if normalized:
                    current["reasoning_effort"] = normalized
                else:
                    current.pop("reasoning_effort", None)

        elif choice == "show_command":
            new_val = questionary.confirm(
                "Show git commands before execution",
                default=show_command,
            ).ask()
            if new_val is not None:
                current["show_command"] = new_val

        elif choice == "skip_confirm":
            new_val = questionary.confirm(
                "Skip confirmation prompts",
                default=skip_confirm,
            ).ask()
            if new_val is not None:
                current["skip_confirm"] = new_val

        elif choice == "commit_emoji":
            new_val = questionary.confirm(
                "Use emoji in commit messages",
                default=commit_emoji,
            ).ask()
            if new_val is not None:
                current.setdefault("commit", {})["emoji"] = new_val

        elif choice == "commit_types":
            new_types = _configure_commit_types(current.get("commit", {}).get("types", []))
            if new_types:
                current.setdefault("commit", {})["types"] = new_types

    # Clean up before saving
    saved = dict(current)
    if not saved.get("apiUrl"):
        saved.pop("apiUrl", None)
    if not saved.get("reasoning_effort"):
        saved.pop("reasoning_effort", None)
    commit_data = saved.get("commit", {})
    if isinstance(commit_data, dict) and not commit_data.get("types"):
        commit_data.pop("types", None)
    if isinstance(commit_data, dict) and not commit_data:
        saved.pop("commit", None)

    global_settings_path.parent.mkdir(parents=True, exist_ok=True)
    global_settings_path.write_text(json.dumps(saved, indent=2, ensure_ascii=False))
    console.print(f"Global settings saved to {global_settings_path}")


def _configure_workspace_settings() -> None:  # noqa: C901, PLR0912, PLR0915
    """Configure workspace-specific settings via a table-based editor."""
    workspace_settings_path = _get_workspace_settings_path()
    global_settings = load_global_settings()
    current = load_workspace_settings()

    console.print(f"\nTarget: {workspace_settings_path}")

    if not questionary.confirm(
        f"Configure workspace settings in {workspace_settings_path}?",
        default=True,
    ).ask():
        return

    while True:
        effective = _get_effective_settings_dict()
        inherited_provider = global_settings.get("provider", "auto")
        inherited_model = global_settings.get("model", "") or PROVIDER_PRESETS.get(inherited_provider, ("", "", DEFAULT_MODEL))[2]
        inherited_api_key = global_settings.get("apiKey", "")
        inherited_api_url = global_settings.get("apiUrl", "")
        inherited_reasoning_effort = _resolve_reasoning_effort_for_display(
            inherited_model,
            global_settings.get("reasoning_effort", ""),
        )
        inherited_show_command = global_settings.get("show_command", True)
        inherited_skip_confirm = global_settings.get("skip_confirm", False)
        inherited_commit_emoji = global_settings.get("commit", {}).get("emoji", False)

        ws_provider = current.get("provider", "")
        ws_api_key = current.get("apiKey", "")
        ws_api_url = current.get("apiUrl", "")
        ws_model = current.get("model", "")
        ws_reasoning_effort = current.get("reasoning_effort", "")
        ws_show_command = current.get("show_command")
        ws_skip_confirm = current.get("skip_confirm")
        ws_commit_emoji = current.get("commit", {}).get("emoji")

        def _label(setting: str, local_val: Any, inherited_val: Any, formatter: Any = str) -> list[tuple[str, str]]:
            label_text = setting.ljust(18)
            if local_val:
                return [("class:ansicyan", label_text), ("", f" → {formatter(local_val)}"), ("class:ansigreen", " (override)")]
            return [("class:ansicyan", label_text), ("", f" → {formatter(inherited_val)}"), ("class:ansigray", " (inherited)")]

        def _bool_label(setting: str, local_val: bool | None, inherited_val: bool) -> list[tuple[str, str]]:
            label_text = setting.ljust(18)
            if local_val is not None:
                return [("class:ansicyan", label_text), ("", f" → {'Yes' if local_val else 'No'}"), ("class:ansigreen", " (override)")]
            return [("class:ansicyan", label_text), ("", f" → {'Yes' if inherited_val else 'No'}"), ("class:ansigray", " (inherited)")]

        # Display table first, then choices
        choice = questionary.select(
            "Select a setting to override:",
            choices=[
                Choice(
                    title=_label("Provider", ws_provider, inherited_provider),
                    value="provider",
                ),
                Choice(
                    title=_label("API Key", ws_api_key, inherited_api_key, _mask_key),
                    value="apiKey",
                ),
                Choice(
                    title=_label("API URL", ws_api_url, inherited_api_url, lambda v: v or "(default)"),
                    value="apiUrl",
                ),
                Choice(
                    title=_label("Model", ws_model, inherited_model),
                    value="model",
                ),
                Choice(
                    title=_label("Reasoning Effort", ws_reasoning_effort, inherited_reasoning_effort, lambda v: v or "(auto)"),
                    value="reasoning_effort",
                ),
                Choice(
                    title=_bool_label("Show Command", ws_show_command, inherited_show_command),
                    value="show_command",
                ),
                Choice(
                    title=_bool_label("Skip Confirm", ws_skip_confirm, inherited_skip_confirm),
                    value="skip_confirm",
                ),
                Choice(
                    title=_bool_label("Use Emoji", ws_commit_emoji, inherited_commit_emoji),
                    value="commit_emoji",
                ),
                Choice(title="─" * 50, disabled="—"),
                Choice(title="Exit", value="exit"),
            ],
        ).ask()

        if choice is None:
            return
        if choice == "exit":
            break

        if choice == "provider":
            new_val = questionary.select(
                f"LLM Provider  (inherited: {inherited_provider})",
                choices=[
                    Choice(title=f"Inherit from global ({inherited_provider})", value=""),
                    *[Choice(title=f"{p}  (default model: {info[2]})", value=p) for p, info in PROVIDER_PRESETS.items()],
                ],
                default=ws_provider,
            ).ask()
            if new_val is not None:
                if new_val:
                    current["provider"] = new_val
                else:
                    current.pop("provider", None)

        elif choice == "apiKey":
            label = "API Key"
            prov = ws_provider or inherited_provider
            if prov in PROVIDER_PRESETS and PROVIDER_PRESETS[prov][1]:
                label = f"API Key  (env: {PROVIDER_PRESETS[prov][1]})"
            display_key = effective.get("apiKey", "")
            if display_key:
                label += f"  (current: {_mask_key(display_key)}, leave empty to inherit)"
            else:
                label += "  (leave empty to inherit)"
            new_val = questionary.text(label, default="").ask()
            if new_val is not None:
                if new_val:
                    current["apiKey"] = new_val
                else:
                    current.pop("apiKey", None)

        elif choice == "apiUrl":
            new_val = questionary.text(
                "API URL  (leave empty to inherit from global)",
                default=ws_api_url,
            ).ask()
            if new_val is not None:
                if new_val:
                    current["apiUrl"] = new_val
                else:
                    current.pop("apiUrl", None)

        elif choice == "model":
            new_val = questionary.text(
                "Model name  (leave empty to inherit from global)",
                default=ws_model,
            ).ask()
            if new_val is not None:
                if new_val:
                    current["model"] = new_val
                else:
                    current.pop("model", None)

        elif choice == "reasoning_effort":
            new_val = questionary.text(
                f"Reasoning effort  ({', '.join(REASONING_EFFORT_CHOICES)})",
                default=ws_reasoning_effort,
                validate=_validate_reasoning_effort,
            ).ask()
            if new_val is not None:
                normalized = _normalize_reasoning_effort(new_val)
                if normalized:
                    current["reasoning_effort"] = normalized
                else:
                    current.pop("reasoning_effort", None)

        elif choice == "show_command":
            new_val = _prompt_workspace_bool_setting(
                "Show git commands before execution",
                current_override=ws_show_command,
                inherited_value=inherited_show_command,
            )
            if new_val is not WORKSPACE_PROMPT_CANCEL:
                if new_val is not None:
                    current["show_command"] = new_val
                else:
                    current.pop("show_command", None)

        elif choice == "skip_confirm":
            new_val = _prompt_workspace_bool_setting(
                "Skip confirmation prompts",
                current_override=ws_skip_confirm,
                inherited_value=inherited_skip_confirm,
            )
            if new_val is not WORKSPACE_PROMPT_CANCEL:
                if new_val is not None:
                    current["skip_confirm"] = new_val
                else:
                    current.pop("skip_confirm", None)

        elif choice == "commit_emoji":
            new_val = _prompt_workspace_bool_setting(
                "Use emoji in commit messages",
                current_override=ws_commit_emoji,
                inherited_value=inherited_commit_emoji,
            )
            if new_val is not WORKSPACE_PROMPT_CANCEL:
                if new_val is not None:
                    current.setdefault("commit", {})["emoji"] = new_val
                elif "commit" in current:
                    current["commit"].pop("emoji", None)
                    if not current["commit"]:
                        current.pop("commit", None)

    # Save only overrides that differ from global
    saved: dict[str, Any] = {}
    if current.get("provider") and current["provider"] != inherited_provider:
        saved["provider"] = current["provider"]
    if current.get("apiKey") and current["apiKey"] != inherited_api_key:
        saved["apiKey"] = current["apiKey"]
    if current.get("apiUrl") and current["apiUrl"] != inherited_api_url:
        saved["apiUrl"] = current["apiUrl"]
    if current.get("model") and current["model"] != inherited_model:
        saved["model"] = current["model"]
    ws_re = current.get("reasoning_effort", "")
    if ws_re and ws_re != inherited_reasoning_effort:
        saved["reasoning_effort"] = ws_re
    if "show_command" in current and current["show_command"] != inherited_show_command:
        saved["show_command"] = current["show_command"]
    if "skip_confirm" in current and current["skip_confirm"] != inherited_skip_confirm:
        saved["skip_confirm"] = current["skip_confirm"]
    ws_emoji = current.get("commit", {}).get("emoji")
    if ws_emoji is not None and ws_emoji != inherited_commit_emoji:
        saved.setdefault("commit", {})["emoji"] = ws_emoji

    workspace_settings_path.parent.mkdir(parents=True, exist_ok=True)
    workspace_settings_path.write_text(json.dumps(saved, indent=2, ensure_ascii=False))
    console.print(f"Workspace settings saved to {workspace_settings_path}")


def _get_effective_settings_dict() -> dict[str, Any]:
    """Return effective settings with defaults applied for display and prompts."""
    effective_settings = load_settings()

    commit_settings: dict[str, Any] = {
        "emoji": effective_settings.commit.emoji,
    }
    if effective_settings.commit.types:
        commit_settings["types"] = [
            {"type": commit_type.type, "emoji": commit_type.emoji} for commit_type in effective_settings.commit.types
        ]

    return {
        "provider": effective_settings.provider,
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
            Choice(title=f"Follow global/default (currently: {current_label})", value=WORKSPACE_BOOL_INHERIT),
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
    return any(hint in model_lower for hint in OPENAI_REASONING_MODEL_HINTS)


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

    console.print("\nConfigure Commit Types")
    console.print("Configure custom commit types and their emojis.")

    use_defaults = questionary.confirm(
        "Use default commit types?",
        default=True,
    ).ask()
    if use_defaults:
        return default_types

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
        console.print("Reset cancelled.")
        return

    if reset_type in ["global", "both"]:
        global_settings_path = _get_global_settings_path()
        if global_settings_path.exists():
            global_settings_path.unlink()
            console.print("Global settings reset successfully!")
        else:
            console.print("Global settings file does not exist.")

    if reset_type in ["workspace", "both"]:
        workspace_settings_path = _get_workspace_settings_path()
        if workspace_settings_path.exists():
            workspace_settings_path.unlink()
            console.print("Workspace settings reset successfully!")
        else:
            console.print("Workspace settings file does not exist.")
