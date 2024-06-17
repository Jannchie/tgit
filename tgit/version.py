import difflib
import os
import re
import subprocess
import tomllib
from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

import inquirer
from rich.panel import Panel

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


def get_prev_version():
    # first, check if there is a file with the version, such as a package.json, pyproject.toml, etc.

    # for nodejs
    if os.path.exists("package.json"):
        import json

        with open("package.json") as f:
            json_data = json.load(f)
            if version := json_data.get("version"):
                return Version.from_str(version)
    elif os.path.exists("pyproject.toml"):

        with open("pyproject.toml", "rb") as f:
            toml_data = tomllib.load(f)
            if version := toml_data.get("project", {}).get("version"):
                return Version.from_str(version)
            if version := toml_data.get("tool", {}).get("poetry", {}).get("version"):
                return Version.from_str(version)
            if version := toml_data.get("tool", {}).get("flit", {}).get("metadata", {}).get("version"):
                return Version.from_str(version)
            if version := toml_data.get("tool", {}).get("setuptools", {}).get("setup_requires", {}).get("version"):
                return Version.from_str(version)

    elif os.path.exists("setup.py"):
        with open("setup.py") as f:
            setup_data = f.read()
            if res := re.search(r"version=['\"]([^'\"]+)['\"]", setup_data):
                return Version.from_str(res[1])

    elif os.path.exists(
        "Cargo.toml",
    ):
        with open("Cargo.toml", "rb") as f:
            cargo_data = tomllib.load(f)
            if version := cargo_data.get("package", {}).get("version"):
                return Version.from_str(version)

    elif os.path.exists("VERSION"):
        with open("VERSION") as f:
            version = f.read().strip()
            return Version.from_str(version)

    elif os.path.exists("VERSION.txt"):
        with open("VERSION.txt") as f:
            version = f.read().strip()
            return Version.from_str(version)

    # if not, check if there is a git tag with the version
    status = subprocess.run(["git", "tag"], capture_output=True)
    if status.returncode == 0:
        tags = status.stdout.decode().split("\n")
        for tag in tags:
            if tag.startswith("v"):
                return Version.from_str(tag[1:])

    # if not, return 0.0.0
    return Version(major=0, minor=0, patch=0)


def handle_version(args: VersionArgs):

    verbose = args.verbose

    # check if there is uncommitted changes
    # status = subprocess.run(["git", "status", "--porcelain"], capture_output=True)
    # if status.returncode != 0:
    #     console.print("Error getting git status")
    #     return
    # if status.stdout:
    #     console.print("There are uncommitted changes, please commit or stash them first")
    #     return

    if verbose > 0:
        console.print("Bumping version...")
        console.print("Getting current version...")
    with console.status("[bold green]Getting current version..."):
        prev_version = get_prev_version()

    console.print(f"Previous version: [cyan bold]{prev_version}")
    # get next version
    next_version = deepcopy(prev_version)
    if not any([args.version, args.patch, args.minor, args.major, args.prepatch, args.preminor, args.premajor]):
        ans = inquirer.prompt(
            [
                inquirer.List(
                    "target",
                    message="Select the version to bump to",
                    choices=[
                        VersionChoice(prev_version, bump) for bump in ["patch", "minor", "major", "prepatch", "preminor", "premajor", "previous", "custom"]
                    ],
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
        if target.bump in ["patch", "prepatch"]:
            next_version.patch += 1
        elif target.bump in ["minor", "preminor"]:
            next_version.minor += 1
            next_version.patch = 0
        elif target.bump in ["major", "premajor"]:
            next_version.major += 1
            next_version.minor = 0
            next_version.patch = 0

        if target.bump in ["prepatch", "preminor", "premajor"]:
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
            if not ans:
                return
            release = ans["identifier"]
            next_version.release = release
        if target.bump == "custom":

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
            version = ans["version"]
            next_version = Version.from_str(version)
        next_version_str = str(next_version)

        # edit files

        if verbose > 0:
            current_path = os.getcwd()
            console.print(f"Current path: [cyan bold]{current_path}")

        # check package.json
        if os.path.exists("package.json"):
            if verbose > 0:
                console.print("Updating package.json")
            with open("package.json", "r") as f:
                package_json = f.read()
            package_json = re.sub(r'"version":\s*".*?"', f'"version": "{next_version_str}"', package_json)

            with open("package.json", "w") as f:
                f.write(package_json)

        if os.path.exists("pyproject.toml"):
            if verbose > 0:
                console.print("Updating pyproject.toml")
            with open("pyproject.toml", "r") as f:
                pyproject_toml = f.read()
            new_pyproject_toml = re.sub(r'version\s*=\s*".*?"', f'version = "{next_version_str}"', pyproject_toml)
            # print diff between the two files
            old_lines = pyproject_toml.splitlines()
            new_lines = new_pyproject_toml.splitlines()
            diff = list(difflib.Differ().compare(old_lines, new_lines))
            print_lines = {}
            for i, line in enumerate(diff):
                if line.startswith("+") or line.startswith("-"):
                    # console.print(f"[green]{line}")
                    for j in range(i - 3, i + 3):
                        if j >= 0 and j < len(diff):
                            print_lines[j] = diff[j][0]

            diffs = []
            for i, line in enumerate(diff):
                line = line.replace("[", "\\[")
                line = line.strip()
                if i in print_lines:
                    if print_lines[i] == "+":
                        diffs.append(f"[green]{line}[/green]")
                    elif print_lines[i] == "-":
                        diffs.append(f"[red]{line}[/red]")
                    elif print_lines[i] == "?":
                        # replace the ? with a space
                        line = line.replace("?", " ")
                        diffs.append(f"[yellow]{line}[/yellow]")
                    else:
                        diffs.append(line)
            if diffs:
                console.print(
                    Panel.fit(
                        "\n".join(diffs),
                        border_style="cyan",
                        title="Diff for pyproject.toml",
                        title_align="left",
                        padding=(1, 4),
                    )
                )

                ok = inquirer.prompt([inquirer.Confirm("continue", message="Do you want to continue?", default=True)])
                if not ok or not ok["continue"]:
                    return

                with open("pyproject.toml", "w") as f:
                    f.write(new_pyproject_toml)

        if os.path.exists("setup.py"):
            if verbose > 0:
                console.print("Updating setup.py")
            with open("setup.py", "r") as f:
                setup_py = f.read()
            new_setup_py = re.sub(r"version=['\"].*?['\"]", f"version='{next_version_str}'", setup_py)
            with open("setup.py", "w") as f:
                f.write(new_setup_py)

        if os.path.exists("Cargo.toml"):
            if verbose > 0:
                console.print("Updating Cargo.toml")
            with open("Cargo.toml", "r") as f:
                cargo_toml = f.read()
            new_cargo_toml = re.sub(r"version\s*=\s*\".*?\"", f'version = "{next_version_str}"', cargo_toml)
            with open("Cargo.toml", "w") as f:
                f.write(new_cargo_toml)

        if os.path.exists("VERSION"):
            if verbose > 0:
                console.print("Updating VERSION")
            with open("VERSION", "w") as f:
                f.write(next_version_str)

        if os.path.exists("VERSION.txt"):
            if verbose > 0:
                console.print("Updating VERSION.txt")
            with open("VERSION.txt", "w") as f:
                f.write(next_version_str)

        git_tag = f"v{next_version_str}"

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
            commands.append("git push")
            commands.append("git push --tag")
        commands_str = "\n".join(commands)
        run_command(commands_str)
        return


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
                release="RELEASE",
            )
        elif bump == "preminor":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor + 1,
                patch=0,
                release="RELEASE",
            )
        elif bump == "prepatch":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor,
                patch=previous_version.patch + 1,
                release="RELEASE",
            )
        elif bump == "previous":
            self.next_version = previous_version

    def __str__(self):
        if "next_version" in self.__dict__:
            return f"{self.bump} -> {self.next_version}"
        else:
            return self.bump


def define_version_parser(subparsers):
    parser_version = subparsers.add_parser("version", help="bump version of the project")
    parser_version.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    parser_version.add_argument("--no-commit", action="store_true", help="do not commit the changes")
    parser_version.add_argument("--no-tag", action="store_true", help="do not create a tag")
    parser_version.add_argument("--no-push", action="store_true", help="do not push the changes")

    # TODO: add option to bump all packages in the monorepo
    # parser_version.add_argument("-r", "--recursive", action="store_true", help="bump all packages in the monorepo")

    # create a mutually exclusive group
    version_group = parser_version.add_mutually_exclusive_group()

    # add arguments to the group
    version_group.add_argument("-p", "--patch", help="patch version", action="store_true")
    version_group.add_argument("-m", "--minor", help="minor version", action="store_true")
    version_group.add_argument("-M", "--major", help="major version", action="store_true")
    version_group.add_argument("-pp", "--prepatch", help="prepatch version", type=str)
    version_group.add_argument("-pm", "--preminor", help="preminor version", type=str)
    version_group.add_argument("-pM", "--premajor", help="premajor version", type=str)
    version_group.add_argument("version", help="version to bump to", type=str, nargs="?")
    parser_version.set_defaults(func=handle_version)
    parser_version.set_defaults(func=handle_version)
    parser_version.set_defaults(func=handle_version)
    parser_version.set_defaults(func=handle_version)
    parser_version.set_defaults(func=handle_version)
    parser_version.set_defaults(func=handle_version)
