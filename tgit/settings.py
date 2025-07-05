from pathlib import Path
from typing import Any

import yaml

settings: dict[str, Any] = {}


def load_global_settings() -> dict[str, Any]:
    global_settings_path = [Path.home() / ".tgit.yaml", Path.home() / ".tgit.yml"]
    return next(
        (yaml.safe_load(path.read_text()) or {} for path in global_settings_path if path.exists()),
        dict[str,Any](),
    )


def set_global_settings(key: str, value: Any) -> None:  # noqa: ANN401
    global_settings_path = [Path.home() / ".tgit.yaml", Path.home() / ".tgit.yml"]
    found = False
    for path in global_settings_path:
        if path.exists():
            file_settings = yaml.safe_load(path.read_text()) or dict[str,Any]()
            file_settings[key] = value
            path.write_text(yaml.dump(file_settings))
            found = True
            break
    if not found:
        file_settings = {key: value}
        global_settings_path[0].write_text(yaml.dump(file_settings))


def load_workspace_settings() -> dict[str, Any]:
    workspace_settings_path = [Path.cwd() / ".tgit.yaml", Path.cwd() / ".tgit.yml"]
    return next(
        (yaml.safe_load(path.read_text()) or {} for path in workspace_settings_path if path.exists()),
        dict[str,Any](),
    )


def load_settings() -> dict[str, Any]:
    global_settings = load_global_settings()
    workspace_settings = load_workspace_settings()
    settings.update(global_settings)
    settings.update(workspace_settings)
    return settings


load_settings()
