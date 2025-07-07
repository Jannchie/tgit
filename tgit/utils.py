import subprocess
import sys

import questionary
import rich
from rich.syntax import Syntax

from tgit.settings import settings

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


def run_command(command: str) -> None:
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
