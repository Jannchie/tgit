import argparse
import os
import re
import shutil
import subprocess
import sys
import tomllib
from copy import deepcopy
from dataclasses import dataclass
from difflib import Differ
from pathlib import Path

import git
import inquirer
from inquirer.questions import Question
from rich.panel import Panel

from tgit.changelog import get_commits, get_git_commits_range, group_commits_by_type
from tgit.settings import settings
from tgit.utils import console, get_commit_command, run_command

semver_regex = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$",
)


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    release: str | None = None
    build: str | None = None

    def __str__(self) -> str:
        if self.release:
            if self.build:
                return f"{self.major}.{self.minor}.{self.patch}-{self.release}+{self.build}"
            return f"{self.major}.{self.minor}.{self.patch}-{self.release}"
        if self.build:
            return f"{self.major}.{self.minor}.{self.patch}+{self.build}"

        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_str(cls, version: str) -> "Version":
        res = semver_regex.match(version)
        if not res:
            msg = "Invalid version format"
            raise ValueError(msg)
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
    def __init__(self, previous_version: Version, bump: str) -> None:
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

    def __str__(self) -> str:
        if "next_version" in self.__dict__:
            return f"{self.bump} ({self.next_version})"
        return self.bump


def get_prev_version(path: str) -> Version:
    path = Path(path).resolve()

    if version := get_version_from_files(path):
        return version

    if version := get_version_from_git(path):
        return version

    return Version(major=0, minor=0, patch=0)


def get_version_from_files(path: Path) -> Version | None:  # noqa: PLR0911
    # sourcery skip: assign-if-exp, reintroduce-else
    if version := get_version_from_package_json(path):
        return version
    if version := get_version_from_pyproject_toml(path):
        return version
    if version := get_version_from_setup_py(path):
        return version
    if version := get_version_from_cargo_toml(path):
        return version
    if version := get_version_from_version_file(path):
        return version
    if version := get_version_from_version_txt(path):
        return version
    return None


def get_version_from_package_json(path: Path) -> Version | None:
    package_json_path = path / "package.json"
    if package_json_path.exists():
        import json

        with package_json_path.open() as f:
            json_data = json.load(f)
            if version := json_data.get("version"):
                return Version.from_str(version)
    return None


def get_version_from_pyproject_toml(path: Path) -> Version | None:
    pyproject_toml_path = path / "pyproject.toml"
    if pyproject_toml_path.exists():
        with pyproject_toml_path.open("rb") as f:
            toml_data = tomllib.load(f)
            if version := toml_data.get("project", {}).get("version"):
                return Version.from_str(version)
            if version := toml_data.get("tool", {}).get("poetry", {}).get("version"):
                return Version.from_str(version)
            if version := toml_data.get("tool", {}).get("flit", {}).get("metadata", {}).get("version"):
                return Version.from_str(version)
            if version := toml_data.get("tool", {}).get("setuptools", {}).get("setup_requires", {}).get("version"):
                return Version.from_str(version)
    return None


def get_version_from_setup_py(path: Path) -> Version | None:
    setup_py_path = path / "setup.py"
    if setup_py_path.exists():
        with setup_py_path.open() as f:
            setup_data = f.read()
            if res := re.search(r"version=['\"]([^'\"]+)['\"]", setup_data):
                return Version.from_str(res[1])
    return None


def get_version_from_cargo_toml(path: Path) -> Version | None:
    cargo_toml_path = path / "Cargo.toml"
    if cargo_toml_path.exists():
        with cargo_toml_path.open("rb") as f:
            cargo_data = tomllib.load(f)
            if version := cargo_data.get("package", {}).get("version"):
                return Version.from_str(version)
    return None


def get_version_from_version_file(path: Path) -> Version | None:
    version_path = path / "VERSION"
    if version_path.exists():
        with version_path.open() as f:
            version = f.read().strip()
            return Version.from_str(version)
    return None


def get_version_from_version_txt(path: Path) -> Version | None:
    version_txt_path = path / "VERSION.txt"
    if version_txt_path.exists():
        with version_txt_path.open() as f:
            version = f.read().strip()
            return Version.from_str(version)
    return None


def get_version_from_git(path: Path) -> Version | None:
    git_executable = shutil.which("git")
    if not git_executable:
        msg = "Git executable not found"
        raise FileNotFoundError(msg)

    status = subprocess.run([git_executable, "tag"], capture_output=True, cwd=path, check=False)  # noqa: S603
    if status.returncode == 0:
        tags = status.stdout.decode().split("\n")
        for tag in tags:
            if tag.startswith("v"):
                return Version.from_str(tag[1:])
    return None


def get_default_bump_by_commits_dict(commits_by_type: dict[str, list[git.Commit]]) -> str:
    # sourcery skip: assign-if-exp, reintroduce-else
    if commits_by_type.get("breaking"):
        return "major"
    if commits_by_type.get("feat"):
        return "minor"
    return "patch"


def handle_version(args: VersionArgs) -> None:
    verbose = args.verbose
    path = args.path
    prev_version = get_current_version(path, verbose)
    reclusive = args.recursive

    if next_version := get_next_version(args, prev_version, verbose):
        update_version_files(args, next_version, verbose, reclusive=reclusive)
        execute_git_commands(args, next_version, verbose)


def get_current_version(path: str, verbose: int) -> Version | None:
    if verbose > 0:
        console.print("Bumping version...")
        console.print("Getting current version...")
    with console.status("[bold green]Getting current version..."):
        prev_version = get_prev_version(path)

    console.print(f"Previous version: [cyan bold]{prev_version}")
    return prev_version


def get_next_version(args: VersionArgs, prev_version: Version, verbose: int) -> Version | None:
    repo = git.Repo(args.path)
    if verbose > 0:
        console.print("Getting commits...")
    from_ref, to_ref = get_git_commits_range(repo, None, None)
    tgit_commits = get_commits(repo, from_ref, to_ref)
    commits_by_type = group_commits_by_type(tgit_commits)
    default_bump = get_default_bump_by_commits_dict(commits_by_type)

    choices = [
        VersionChoice(prev_version, bump) for bump in ["patch", "minor", "major", "prepatch", "preminor", "premajor", "previous", "custom"]
    ]
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
            ],
        )
        if not ans:
            return None

        target = ans["target"]
        # assert isinstance(target, VersionChoice)
        if not isinstance(target, VersionChoice):
            msg = "Type assertion failed"
            raise AssertionError(msg)
        if verbose > 0:
            console.print(f"Selected target: [cyan bold]{target}")

        # bump the version
        bump_version(target, next_version)

        if target.bump in ["prepatch", "preminor", "premajor"]:
            if release := get_pre_release_identifier():
                next_version.release = release
            else:
                return None
        if target.bump == "custom":
            if custom_version := get_custom_version():
                next_version = custom_version
            else:
                return None
    return next_version


def bump_version(target: VersionChoice, next_version: Version) -> None:
    if target.bump in ["patch", "prepatch"]:
        next_version.patch += 1
    elif target.bump in ["minor", "preminor"]:
        next_version.minor += 1
        next_version.patch = 0
    elif target.bump in ["major", "premajor"]:
        next_version.major += 1
        next_version.minor = 0
        next_version.patch = 0


def get_pre_release_identifier() -> str | None:
    ans = inquirer.prompt(
        [
            inquirer.Text(
                "identifier",
                message="Enter the pre-release identifier",
                default="alpha",
                validate=lambda _, x: re.match(r"[0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*", x).group() == x,
            ),
        ],
    )
    return ans["identifier"] if ans else None


def get_custom_version() -> Version | None:
    def validate_semver(_: Question, x: str) -> bool:
        res = semver_regex.match(x)
        return res and res.group() == x

    ans = inquirer.prompt(
        [
            inquirer.Text(
                "version",
                message="Enter the version",
                validate=validate_semver,
            ),
        ],
    )
    if not ans:
        return None
    version = ans["version"]
    return Version.from_str(version)


def update_version_files(
    args: VersionArgs,
    next_version: Version,
    verbose: int,
    *,
    reclusive: bool,
) -> None:
    # sourcery skip: merge-comparisons, merge-duplicate-blocks, remove-redundant-if
    next_version_str = str(next_version)

    current_path = Path(args.path).resolve()
    if verbose > 0:
        console.print(f"Current path: [cyan bold]{current_path}")

    if reclusive:
        # 获取当前目录及其子目录下，所有名称在上述列表中的文件
        # 使用os.walk()函数，可以遍历指定目录下的所有子目录和文件
        filenames = ["package.json", "pyproject.toml", "setup.py", "Cargo.toml", "VERSION", "VERSION.txt", "build.gradle.kts"]
        # 需要忽略 node_modules 目录
        for root, dirs, files in os.walk(current_path):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            for file in files:
                if file in filenames:
                    # file_path = os.path.join(root, file)
                    file_path = Path(root) / file
                    update_version_in_file(verbose, next_version_str, file, file_path)
    else:
        update_file_in_root(next_version_str, verbose)


def update_version_in_file(verbose: int, next_version_str: str, file: str, file_path: Path) -> None:
    # sourcery skip: collection-into-set, merge-duplicate-blocks, remove-redundant-if
    if file == "package.json":
        update_file(file_path, r'"version":\s*".*?"', f'"version": "{next_version_str}"', verbose, show_diff=False)
    elif file in ("pyproject.toml", "build.gradle.kts"):
        update_file(file_path, r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose, show_diff=False)
    elif file == "setup.py":
        update_file(file_path, r"version=['\"].*?['\"]", f"version='{next_version_str}'", verbose, show_diff=False)
    elif file == "Cargo.toml":
        update_file(file_path, r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose, show_diff=False)
    elif file in ("VERSION", "VERSION.txt"):
        update_file(file_path, None, next_version_str, verbose, show_diff=False)


def update_file_in_root(next_version_str: str, verbose: int) -> None:
    update_file("package.json", r'"version":\s*".*?"', f'"version": "{next_version_str}"', verbose)
    update_file("pyproject.toml", r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose)
    update_file("setup.py", r"version=['\"].*?['\"]", f"version='{next_version_str}'", verbose)
    update_file("Cargo.toml", r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose)
    update_file("build.gradle.kts", r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose)
    update_file("VERSION", None, next_version_str, verbose)
    update_file("VERSION.txt", None, next_version_str, verbose)


def update_file(filename: str, search_pattern: str | None, replace_text: str, verbose: int, *, show_diff: bool = True) -> None:
    filename = Path(filename)
    if not filename.exists():
        return
    if verbose > 0:
        console.print(f"Updating {filename}")
    with filename.open() as f:
        content = f.read()
    new_content = re.sub(search_pattern, replace_text, content) if search_pattern else replace_text
    if show_diff:
        show_file_diff(content, new_content, filename)
    with filename.open("w") as f:
        f.write(new_content)


def show_file_diff(old_content: str, new_content: str, filename: str) -> None:
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    diff = list(Differ().compare(old_lines, new_lines))
    print_lines = extract_context_lines(diff)

    diffs = []
    format_diff_lines(diff, print_lines, diffs)
    if diffs:
        console.print(
            Panel.fit(
                "\n".join(diffs),
                border_style="cyan",
                title=f"Diff for {filename}",
                title_align="left",
                padding=(1, 4),
            ),
        )
        ok = inquirer.prompt([inquirer.Confirm("continue", message="Do you want to continue?", default=True)])
        if not ok or not ok["continue"]:
            sys.exit()


def extract_context_lines(diff: list[str]) -> dict[int, str]:
    print_lines = {}
    for i, line in enumerate(diff):
        if line.startswith(("+", "-")):
            for j in range(i - 3, i + 3):
                if j >= 0 and j < len(diff):
                    print_lines[j] = diff[j][0]
    return print_lines


def format_diff_lines(diff: list[str], print_lines: dict[int, str], diffs: list[str]) -> None:
    for i, line in enumerate(diff):
        new_line = line.replace("[", "\\[")
        if i in print_lines:
            if print_lines[i] == "+":
                diffs.append(f"[green]{line}[/green]")
            elif print_lines[i] == "-":
                diffs.append(f"[red]{line}[/red]")
            elif print_lines[i] == "?":
                new_line = line.replace("?", " ")
                new_line = line.replace("\n", "")
                diffs.append(f"[yellow]{new_line}[/yellow]")
            else:
                diffs.append(new_line)


def execute_git_commands(args: VersionArgs, next_version: Version, verbose: int) -> None:
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


def define_version_parser(subparsers: argparse._SubParsersAction) -> None:
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
