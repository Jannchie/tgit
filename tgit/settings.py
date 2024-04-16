from pathlib import Path

import yaml

settings = {}


def load_global_settings():
    global_settings_path = [Path.home() / ".tgit.yaml", Path.home() / ".tgit.yml"]
    return next(
        (yaml.safe_load(path.read_text()) for path in global_settings_path if path.exists()),
        None,
    )


def load_workspace_settings():
    workspace_settings_path = [Path.cwd() / ".tgit.yaml", Path.cwd() / ".tgit.yml"]
    return next(
        (yaml.safe_load(path.read_text()) for path in workspace_settings_path if path.exists()),
        None,
    )


def load_settings():
    global_settings = load_global_settings()
    workspace_settings = load_workspace_settings()
    settings.update(global_settings or {})
    settings.update(workspace_settings or {})
    return settings


load_settings()
