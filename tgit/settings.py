from pathlib import Path

import yaml

settings = {}


def load_global_settings() -> dict:
    global_settings_path = [Path.home() / ".tgit.yaml", Path.home() / ".tgit.yml"]
    return next(
        (yaml.safe_load(path.read_text()) for path in global_settings_path if path.exists()),
        None,
    )


def set_global_settings(key: str, value: str) -> None:
    global_settings_path = [Path.home() / ".tgit.yaml", Path.home() / ".tgit.yml"]
    found = False
    for path in global_settings_path:
        if path.exists():
            settings = yaml.safe_load(path.read_text())
            settings[key] = value
            path.write_text(yaml.dump(settings))
            found = True
            break
    if not found:
        settings = {key: value}
        global_settings_path[0].write_text(yaml.dump(settings))


def load_workspace_settings() -> dict:
    workspace_settings_path = [Path.cwd() / ".tgit.yaml", Path.cwd() / ".tgit.yml"]
    return next(
        (yaml.safe_load(path.read_text()) for path in workspace_settings_path if path.exists()),
        None,
    )


def load_settings() -> dict:
    global_settings = load_global_settings()
    workspace_settings = load_workspace_settings()
    settings.update(global_settings or {})
    settings.update(workspace_settings or {})
    return settings


load_settings()
