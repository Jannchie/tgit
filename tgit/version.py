import os
import re
from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

import inquirer

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
        if self.release and self.build:
            return f"{self.major}.{self.minor}.{self.patch}-{self.release}+{self.build}"
        if self.release:
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
    # if not, check if there is a git tag with the version
    # if not, return 0.0.0
    return Version(major=0, minor=0, patch=0)


def handle_version(args: VersionArgs):
    verbose = args.verbose

    if verbose > 0:
        console.print("Bumping version...")
        console.print("Getting current version...")

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
                    choices=[VersionChoice(prev_version, bump) for bump in ["patch", "minor", "major", "prepatch", "preminor", "premajor", "custom"]],
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
                console.print(f"Updating package.json")
            with open("package.json", "r") as f:
                package_json = f.read()
            package_json = re.sub(r'"version":\s*".*?"', f'"version": "{next_version_str}"', package_json)

            with open("package.json", "w") as f:
                f.write(package_json)

        git_tag = f"v{next_version_str}"

        commands = []
        if args.no_commit:
            if verbose > 0:
                console.print(f"Skipping commit")
        else:
            commands.append(get_commit_command("version", None, f"{git_tag}", use_emojis=True))

        if args.no_tag:
            if verbose > 0:
                console.print(f"Skipping tag")
        else:
            commands.append(f"git tag {git_tag} -m 'Release {git_tag}'")

        if args.no_push:
            if verbose > 0:
                console.print(f"Skipping push")
        else:
            commands.append(f"git push")
            commands.append(f"git push {git_tag}")
        commands_str = "\n".join(commands)
        run_command(commands_str)
        return
    pass


class VersionChoice:
    def __init__(self, previous_version: Version, bump: str):
        self.previous_version = previous_version
        self.bump = bump
        if bump == "patch":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor,
                patch=previous_version.patch + 1,
            )
        elif bump == "minor":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor + 1,
                patch=0,
            )
        elif bump == "major":
            self.next_version = Version(
                major=previous_version.major + 1,
                minor=0,
                patch=0,
            )
        elif bump == "prepatch":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor,
                patch=previous_version.patch + 1,
                release="RELEASE",
            )
        elif bump == "preminor":
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor + 1,
                patch=0,
                release="RELEASE",
            )
        elif bump == "premajor":
            self.next_version = Version(
                major=previous_version.major + 1,
                minor=0,
                patch=0,
                release="RELEASE",
            )

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
