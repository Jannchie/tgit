import os
import re
import subprocess
import tomllib
from copy import deepcopy
from dataclasses import dataclass
from difflib import Differ
from typing import Optional

import git
import inquirer
from rich.panel import Panel

from tgit.changelog import get_commits, get_git_commits_range, group_commits_by_type
from tgit.settings import settings
from tgit.utils import console, get_commit_command, run_command

semver_regex = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    release: Optional[str] = None
    build: Optional[str] = None

    def __str__(self):
        if self.release:
            if self.build:
                return f"{self.major}.{self.minor}.{self.patch}-{self.release}+{self.build}"
            return f"{self.major}.{self.minor}.{self.patch}-{self.release}"
        if self.build:
            return f"{self.major}.{self.minor}.{self.patch}+{self.build}"

        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_str(cls, version: str):
        res = semver_regex.match(version)
        if not res:
            raise ValueError("Invalid version format")
        groups = res.groups()
        major, minor, patch = map(int, groups[:3])
        release = groups[3]
        build = groups[4]
        return cls(major, minor, patch, release, build)


@dataclass
class VersionArgs:
    version: str
    verbose: int
    no_commit: bool
    no_tag: bool
    no_push: bool
    patch: bool
    minor: bool
    major: bool
    prepatch: str
    preminor: str
    premajor: str
    recursive: bool
    custom: str
    path: str


class VersionChoice:
    def __init__(self, previous_version: Version, bump: str):
        self.previous_version = previous_version
        self.bump = bump
        if bump == "major":
            self.next_version = Version(
                major=previous_version.major + 1,
                minor=0,
                patch=0,
            )
        elif bump == "minor":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor + 1,
                patch=0,
            )
        elif bump == "patch":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor,
                patch=previous_version.patch + 1,
            )
        elif bump == "premajor":
            self.next_version = Version(
                major=previous_version.major + 1,
                minor=0,
                patch=0,
                release="{RELEASE}",
            )
        elif bump == "preminor":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor + 1,
                patch=0,
                release="{RELEASE}",
            )
        elif bump == "prepatch":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor,
                patch=previous_version.patch + 1,
                release="{RELEASE}",
            )
        elif bump == "previous":
            self.next_version = previous_version

    def __str__(self):
        if "next_version" in self.__dict__:
            return f"{self.bump} ({self.next_version})"
        else:
            return self.bump


def get_prev_version(path: str) -> Version:
    # first, check if there is a file with the version, such as a package.json, pyproject.toml, etc.

    # for nodejs
    if os.path.exists(os.path.join(path, "package.json")):
        import json

        with open(os.path.join(path, "package.json")) as f:
            json_data = json.load(f)
            if version := json_data.get("version"):
                return Version.from_str(version)
    elif os.path.exists(os.path.join(path, "pyproject.toml")):

        with open(os.path.join(path, "pyproject.toml"), "rb") as f:
            toml_data = tomllib.load(f)
            if version := toml_data.get("project", {}).get("version"):
                return Version.from_str(version)
            if version := toml_data.get("tool", {}).get("poetry", {}).get("version"):
                return Version.from_str(version)
            if version := toml_data.get("tool", {}).get("flit", {}).get("metadata", {}).get("version"):
                return Version.from_str(version)
            if version := toml_data.get("tool", {}).get("setuptools", {}).get("setup_requires", {}).get("version"):
                return Version.from_str(version)

    elif os.path.exists(os.path.join(path, "setup.py")):
        with open(os.path.join(path, "setup.py")) as f:
            setup_data = f.read()
            if res := re.search(r"version=['\"]([^'\"]+)['\"]", setup_data):
                return Version.from_str(res[1])

    elif os.path.exists(os.path.join(path, "Cargo.toml")):
        with open(os.path.join(path, "Cargo.toml"), "rb") as f:
            cargo_data = tomllib.load(f)
            if version := cargo_data.get("package", {}).get("version"):
                return Version.from_str(version)

    elif os.path.exists(os.path.join(path, "VERSION")):
        with open(os.path.join(path, "VERSION")) as f:
            version = f.read().strip()
            return Version.from_str(version)

    elif os.path.exists(os.path.join(path, "VERSION.txt")):
        with open(os.path.join(path, "VERSION.txt")) as f:
            version = f.read().strip()
            return Version.from_str(version)

    # if not, check if there is a git tag with the version
    status = subprocess.run(["git", "tag"], capture_output=True, cwd=path)
    if status.returncode == 0:
        tags = status.stdout.decode().split("\n")
        for tag in tags:
            if tag.startswith("v"):
                return Version.from_str(tag[1:])

    # if not, return 0.0.0
    return Version(major=0, minor=0, patch=0)


def get_default_bump_by_commits_dict(commits_by_type: dict[str, list[git.Commit]]) -> str:
    if commits_by_type.get("breaking"):
        return "major"
    elif commits_by_type.get("feat"):
        return "minor"
    return "patch"


def handle_version(args: VersionArgs):
    verbose = args.verbose
    path = args.path
    prev_version = get_current_version(path, verbose)
    reclusive = args.recursive

    if next_version := get_next_version(args, prev_version, verbose):
        update_version_files(args, next_version, reclusive, verbose)
        execute_git_commands(args, next_version, verbose)


def get_current_version(path: str, verbose: int) -> Optional[Version]:
    if verbose > 0:
        console.print("Bumping version...")
        console.print("Getting current version...")
    with console.status("[bold green]Getting current version..."):
        prev_version = get_prev_version(path)

    console.print(f"Previous version: [cyan bold]{prev_version}")
    return prev_version


def get_next_version(args: VersionArgs, prev_version: Version, verbose: int) -> Optional[Version]:

    repo = git.Repo(args.path)
    if verbose > 0:
        console.print("Getting commits...")
    from_ref, to_ref = get_git_commits_range(repo, None, None)
    tgit_commits = get_commits(repo, from_ref, to_ref)
    commits_by_type = group_commits_by_type(tgit_commits)
    default_bump = get_default_bump_by_commits_dict(commits_by_type)

    choices = [VersionChoice(prev_version, bump) for bump in ["patch", "minor", "major", "prepatch", "preminor", "premajor", "previous", "custom"]]
    default_choice = next((choice for choice in choices if choice.bump == default_bump), None)
    next_version = deepcopy(prev_version)

    console.print(f"Auto bump based on commits: [cyan bold]{default_bump}")

    if not any([args.custom, args.patch, args.minor, args.major, args.prepatch, args.preminor, args.premajor]):
        ans = inquirer.prompt(
            [
                inquirer.List(
                    "target",
                    message="Select the version to bump to",
                    choices=choices,
                    default=default_choice,
                    carousel=True,
                ),
            ]
        )
        if not ans:
            return

        target = ans["target"]
        assert isinstance(target, VersionChoice)
        if verbose > 0:
            console.print(f"Selected target: [cyan bold]{target}")

        # bump the version
        bump_version(target, next_version)

        if target.bump in ["prepatch", "preminor", "premajor"]:
            if release := get_pre_release_identifier():
                next_version.release = release
            else:
                return
        if target.bump == "custom":
            if custom_version := get_custom_version():
                next_version = custom_version
            else:
                return
    return next_version


def bump_version(target: VersionChoice, next_version: Version):
    if target.bump in ["patch", "prepatch"]:
        next_version.patch += 1
    elif target.bump in ["minor", "preminor"]:
        next_version.minor += 1
        next_version.patch = 0
    elif target.bump in ["major", "premajor"]:
        next_version.major += 1
        next_version.minor = 0
        next_version.patch = 0


def get_pre_release_identifier() -> Optional[str]:
    ans = inquirer.prompt(
        [
            inquirer.Text(
                "identifier",
                message="Enter the pre-release identifier",
                default="alpha",
                validate=lambda _, x: re.match(r"[0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*", x).group() == x,
            )
        ]
    )
    return ans["identifier"] if ans else None


def get_custom_version() -> Optional[Version]:
    def validate_semver(_, x):
        res = semver_regex.match(x)
        return res and res.group() == x

    ans = inquirer.prompt(
        [
            inquirer.Text(
                "version",
                message="Enter the version",
                validate=validate_semver,
            )
        ]
    )
    if not ans:
        return None
    version = ans["version"]
    return Version.from_str(version)


def update_version_files(args: VersionArgs, next_version: Version, reclusive: bool, verbose: int):
    next_version_str = str(next_version)

    current_path = os.path.abspath(args.path)
    if verbose > 0:
        console.print(f"Current path: [cyan bold]{current_path}")

    if reclusive:
        # 获取当前目录及其子目录下，所有名称在上述列表中的文件
        # 使用os.walk()函数，可以遍历指定目录下的所有子目录和文件
        filenames = ["package.json", "pyproject.toml", "setup.py", "Cargo.toml", "VERSION", "VERSION.txt"]
        # 需要忽略 node_modules 目录
        for root, dirs, files in os.walk(current_path):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            for file in files:
                if file in filenames:
                    file_path = os.path.join(root, file)
                    if file == "package.json":
                        update_file(file_path, r'"version":\s*".*?"', f'"version": "{next_version_str}"', verbose, show_diff=False)
                    elif file == "pyproject.toml":
                        update_file(file_path, r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose, show_diff=False)
                    elif file == "setup.py":
                        update_file(file_path, r"version=['\"].*?['\"]", f"version='{next_version_str}'", verbose, show_diff=False)
                    elif file == "Cargo.toml":
                        update_file(file_path, r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose, show_diff=False)
                    elif file == "VERSION":
                        update_file(file_path, None, next_version_str, verbose, show_diff=False)
                    elif file == "VERSION.txt":
                        update_file(file_path, None, next_version_str, verbose, show_diff=False)
    else:
        update_file_in_root(next_version_str, verbose)


def update_file_in_root(next_version_str, verbose):
    update_file("package.json", r'"version":\s*".*?"', f'"version": "{next_version_str}"', verbose)
    update_file("pyproject.toml", r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose)
    update_file("setup.py", r"version=['\"].*?['\"]", f"version='{next_version_str}'", verbose)
    update_file("Cargo.toml", r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose)
    update_file("VERSION", None, next_version_str, verbose)
    update_file("VERSION.txt", None, next_version_str, verbose)


def update_file(filename: str, search_pattern: Optional[str], replace_text: str, verbose: int, show_diff: bool = True):
    if not os.path.exists(filename):
        return
    if verbose > 0:
        console.print(f"Updating {filename}")
    with open(filename, "r") as f:
        content = f.read()
    new_content = re.sub(search_pattern, replace_text, content) if search_pattern else replace_text
    if show_diff:
        show_file_diff(content, new_content, filename)
    with open(filename, "w") as f:
        f.write(new_content)


def show_file_diff(old_content: str, new_content: str, filename: str):
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    diff = list(Differ().compare(old_lines, new_lines))
    print_lines = {}
    for i, line in enumerate(diff):
        if line.startswith("+") or line.startswith("-"):
            for j in range(i - 3, i + 3):
                if j >= 0 and j < len(diff):
                    print_lines[j] = diff[j][0]

    diffs = []
    for i, line in enumerate(diff):
        line = line.replace("[", "\\[")
        if i in print_lines:
            if print_lines[i] == "+":
                diffs.append(f"[green]{line}[/green]")
            elif print_lines[i] == "-":
                diffs.append(f"[red]{line}[/red]")
            elif print_lines[i] == "?":
                line = line.replace("?", " ")
                line = line.replace("\n", "")
                diffs.append(f"[yellow]{line}[/yellow]")
            else:
                diffs.append(line)
    if diffs:
        console.print(
            Panel.fit(
                "\n".join(diffs),
                border_style="cyan",
                title=f"Diff for {filename}",
                title_align="left",
                padding=(1, 4),
            )
        )

        ok = inquirer.prompt([inquirer.Confirm("continue", message="Do you want to continue?", default=True)])
        if not ok or not ok["continue"]:
            exit()


def execute_git_commands(args: VersionArgs, next_version: Version, verbose: int):
    git_tag = f"v{next_version}"

    commands = []
    if args.no_commit:
        if verbose > 0:
            console.print("Skipping commit")
    else:
        commands.append("git add .")
        use_emoji = settings.get("commit", {}).get("emoji", False)
        commands.append(get_commit_command("version", None, f"{git_tag}", use_emoji=use_emoji))

    if args.no_tag:
        if verbose > 0:
            console.print("Skipping tag")
    else:
        commands.append(f"git tag {git_tag}")

    if args.no_push:
        if verbose > 0:
            console.print("Skipping push")
    else:
        commands.extend(("git push", "git push --tag"))
    commands_str = "\n".join(commands)
    run_command(commands_str)


def define_version_parser(subparsers):
    parser_version = subparsers.add_parser("version", help="bump version of the project")
    parser_version.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    parser_version.add_argument("--no-commit", action="store_true", help="do not commit the changes")
    parser_version.add_argument("--no-tag", action="store_true", help="do not create a tag")
    parser_version.add_argument("--no-push", action="store_true", help="do not push the changes")

    # add option to bump all packages in the monorepo
    parser_version.add_argument("-r", "--recursive", action="store_true", help="bump all packages in the monorepo")

    # create a mutually exclusive group
    version_group = parser_version.add_mutually_exclusive_group()

    # add arguments to the group
    version_group.add_argument("-p", "--patch", help="patch version", action="store_true")
    version_group.add_argument("-m", "--minor", help="minor version", action="store_true")
    version_group.add_argument("-M", "--major", help="major version", action="store_true")
    version_group.add_argument("-pp", "--prepatch", help="prepatch version", type=str)
    version_group.add_argument("-pm", "--preminor", help="preminor version", type=str)
    version_group.add_argument("-pM", "--premajor", help="premajor version", type=str)
    version_group.add_argument("--custom", help="custom version to bump to", action="store_true")
    version_group.add_argument("path", help="path to the file to update", nargs="?", default=".")

    parser_version.set_defaults(func=handle_version)
