import json
from pathlib import Path
from typing import Any

from tgit.types import CommitSettings, CommitType, TGitSettings

settings: TGitSettings = TGitSettings()


def load_global_settings() -> dict[str, Any]:
    global_settings_path = Path.home() / ".tgit" / "settings.json"
    if global_settings_path.exists():
        return json.loads(global_settings_path.read_text()) or {}
    return {}


def _dict_to_settings(data: dict[str, Any]) -> TGitSettings:
    """Convert dict to TGitSettings dataclass."""
    commit_data = data.get("commit", {})
    commit_types = [
        CommitType(
            type=type_data.get("type", ""),
            emoji=type_data.get("emoji", ""),
        )
        for type_data in commit_data.get("types", [])
    ]

    commit_settings = CommitSettings(
        emoji=commit_data.get("emoji", False),
        types=commit_types,
    )

    return TGitSettings(
        commit=commit_settings,
        api_key=data.get("apiKey", ""),
        api_url=data.get("apiUrl", ""),
        model=data.get("model", ""),
        show_command=data.get("show_command", True),
        skip_confirm=data.get("skip_confirm", False),
    )


def set_global_settings(key: str, value: Any) -> None:  # noqa: ANN401
    global_settings_path = Path.home() / ".tgit" / "settings.json"
    global_settings_path.parent.mkdir(parents=True, exist_ok=True)

    file_settings = json.loads(global_settings_path.read_text()) or {} if global_settings_path.exists() else {} # type: ignore

    file_settings[key] = value
    global_settings_path.write_text(json.dumps(file_settings, indent=2))


def load_workspace_settings() -> dict[str, Any]:
    workspace_settings_paths = [
        Path.cwd() / ".tgit" / "settings.local.json",
        Path.cwd() / ".tgit" / "settings.json",
    ]

    for path in workspace_settings_paths:
        if path.exists():
            return json.loads(path.read_text()) or {}

    return {}


def _merge_settings(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge two settings dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_settings(result[key], value) # type: ignore
        else:
            result[key] = value
    return result


def load_settings() -> TGitSettings:
    global settings  # noqa: PLW0603
    global_settings = load_global_settings()
    workspace_settings = load_workspace_settings()
    merged_settings = _merge_settings(global_settings, workspace_settings)
    settings = _dict_to_settings(merged_settings)
    return settings


load_settings()
