import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import questionary
import rich
from rich.syntax import Syntax

from tgit.types import CommitSettings, CommitType, TGitSettings

console = rich.get_console()


type_emojis = {
    "feat": ":sparkles:",
    "fix": ":adhesive_bandage:",
    "chore": ":wrench:",
    "docs": ":page_with_curl:",
    "style": ":lipstick:",
    "refactor": ":hammer:",
    "perf": ":zap:",
    "test": ":rotating_light:",
    "version": ":bookmark:",
    "ci": ":construction_worker:",
}


def get_commit_command(
    commit_type: str,
    commit_scope: str | None,
    commit_msg: str,
    *,
    use_emoji: bool = False,
    is_breaking: bool = False,
) -> str:
    if commit_type.endswith("!"):
        commit_type = commit_type[:-1]
        is_breaking = True
        breaking_str = "!"
    else:
        breaking_str = "!" if is_breaking else ""
    if commit_scope is None:
        msg = f"{commit_type}{breaking_str}: {commit_msg}"
    else:
        msg = f"{commit_type}({commit_scope}){breaking_str}: {commit_msg}"
    if use_emoji:
        msg = f"{type_emojis.get(commit_type, ':wrench:')} {msg}"
    return f'git commit -m "{msg}"'


def simple_run_command(command: str) -> None:
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # noqa: S602
    stdout, stderr = process.communicate()
    if stderr != b"" and process.returncode != 0:
        sys.stderr.write(stderr.decode())
    if stdout != b"":
        sys.stdout.write(stdout.decode())


def run_command(settings: TGitSettings, command: str) -> None:
    if settings.show_command:
        console.print("\n[cyan]The following command will be executed:[/cyan]")
        console.print(Syntax(f"\n{command}\n", "bash", line_numbers=False, theme="github-dark", background_color="default", word_wrap=True))
    if not settings.skip_confirm:
        ok = questionary.confirm("Do you want to continue?", default=True).ask()
        if not ok:
            return
        console.print()

    with console.status("[bold green]Executing...") as status:
        # use subprocess to run the command
        commands = command.split("\n")
        for cmd in commands:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # noqa: S602
            status.update(f"[bold green]Executing: {command}[/bold green]")

            # get the output and error
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                status.update("[bold red]Error[/bold red]")
            else:
                status.update("[bold green]Execute successful[/bold green]")
            if stderr != b"" and process.returncode != 0:
                sys.stderr.write(stderr.decode())
            if stdout != b"":
                sys.stdout.write(stdout.decode())


def load_global_settings() -> dict[str, Any]:
    global_settings_path = Path.home() / ".tgit" / "settings.json"
    if global_settings_path.exists():
        return json.loads(global_settings_path.read_text()) or {}
    return {}


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
            result[key] = _merge_settings(result[key], value)  # type: ignore
        else:
            result[key] = value
    return result


def load_settings() -> TGitSettings:
    global_settings = load_global_settings()
    workspace_settings = load_workspace_settings()
    merged_settings = _merge_settings(global_settings, workspace_settings)
    return _dict_to_settings(merged_settings)


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

    file_settings = json.loads(global_settings_path.read_text()) or {} if global_settings_path.exists() else {}  # type: ignore

    file_settings[key] = value
    global_settings_path.write_text(json.dumps(file_settings, indent=2))
