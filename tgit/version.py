import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from argparse import Namespace
from copy import deepcopy
from dataclasses import dataclass
from difflib import Differ
from pathlib import Path

import click
import git
import questionary
from questionary import Choice

from tgit.changelog import get_commits, get_git_commits_range, group_commits_by_type, handle_changelog
from tgit.shared import settings
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
        elif bump == "release":
            # Remove prerelease suffix to create a stable release
            self.next_version = Version(
                major=previous_version.major,
                minor=previous_version.minor,
                patch=previous_version.patch,
            )
        elif bump == "previous":
            self.next_version = previous_version

    def __str__(self) -> str:
        if "next_version" in self.__dict__:
            return f"{self.bump} ({self.next_version})"
        return self.bump


def get_prev_version(path: str) -> Version:
    path_obj = Path(path).resolve()

    if version := get_version_from_files(path_obj):
        return version

    if version := get_version_from_git(path_obj):
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
        with package_json_path.open() as f:
            json_data = json.load(f)
            if version := json_data.get("version"):
                try:
                    return Version.from_str(version)
                except ValueError:
                    return None
    return None


def get_version_from_pyproject_toml(path: Path) -> Version | None:
    pyproject_toml_path = path / "pyproject.toml"
    if not pyproject_toml_path.exists():
        return None

    with pyproject_toml_path.open("rb") as f:
        toml_data = tomllib.load(f)

    version_paths = [
        toml_data.get("project", {}).get("version"),
        toml_data.get("tool", {}).get("poetry", {}).get("version"),
        toml_data.get("tool", {}).get("flit", {}).get("metadata", {}).get("version"),
        toml_data.get("tool", {}).get("setuptools", {}).get("setup_requires", {}).get("version"),
    ]

    for version in version_paths:
        if version:
            try:
                return Version.from_str(version)
            except ValueError:
                continue

    return None


def get_version_from_setup_py(path: Path) -> Version | None:
    setup_py_path = path / "setup.py"
    if setup_py_path.exists():
        with setup_py_path.open() as f:
            setup_data = f.read()
            if res := re.search(r"version=['\"]([^'\"]+)['\"]", setup_data):
                try:
                    return Version.from_str(res[1])
                except ValueError:
                    return None
    return None


def get_version_from_cargo_toml(directory_path: Path) -> Version | None:
    """
    Safely reads and parses the package version from a Cargo.toml file
    located in the specified directory.

    Args:
        directory_path: The path to the directory containing the Cargo.toml file.

    Returns:
        A packaging.version.Version object if the version is found and valid,
        otherwise None. Returns None if the file doesn't exist, is unreadable,
        is invalid TOML, or lacks a valid package version string.
    """
    cargo_toml_path = directory_path / "Cargo.toml"

    # 1. Check if the file exists and is a file
    if not cargo_toml_path.is_file():
        console.print(f"Cargo.toml not found or is not a file at: {cargo_toml_path}")
        return None

    # 2. Load and parse the TOML file
    try:
        with cargo_toml_path.open("rb") as f:
            cargo_data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError) as e:
        console.print(f"Could not read or parse TOML file {cargo_toml_path}: {e}")
        return None

    # 3. Safely access the package table and version string
    package_data = cargo_data.get("package")
    if not isinstance(package_data, dict):
        console.print(f"Missing or invalid [package] table in {cargo_toml_path}")
        return None

    version_str = package_data.get("version")  # type: ignore
    if not isinstance(version_str, str) or not version_str:  # Check if it's a non-empty string
        console.print(f"Missing, empty, or invalid 'version' string in [package] table of {cargo_toml_path}")
        return None

    # 4. Parse and return the version
    try:
        return Version.from_str(version_str)
    except ValueError:
        return None


def get_version_from_version_file(path: Path) -> Version | None:
    version_path = path / "VERSION"
    if version_path.exists():
        with version_path.open() as f:
            version = f.read().strip()
            try:
                return Version.from_str(version)
            except ValueError:
                return None
    return None


def get_version_from_version_txt(path: Path) -> Version | None:
    version_txt_path = path / "VERSION.txt"
    if version_txt_path.exists():
        with version_txt_path.open() as f:
            version = f.read().strip()
            try:
                return Version.from_str(version)
            except ValueError:
                return None
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
                try:
                    return Version.from_str(tag[1:])
                except ValueError:
                    continue
    return None


def get_default_bump_by_commits_dict(commits_by_type: dict[str, list[git.Commit]], prev_version: Version | None = None) -> str:
    # v0.x.x breaking change 只 bump minor，v1+ 才 bump major
    if prev_version and prev_version.major == 0:
        if commits_by_type.get("breaking"):
            return "minor"
    elif commits_by_type.get("breaking"):
        return "major"
    if commits_by_type.get("feat"):
        return "minor"
    return "patch"


def _parse_gitignore(gitignore_path: Path) -> list[str]:
    """Parse gitignore file and return list of patterns."""
    if not gitignore_path.exists():
        return []

    patterns = []
    try:
        with gitignore_path.open(encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    except (OSError, UnicodeDecodeError):
        pass
    return patterns


def _should_ignore_path(path: Path, root_path: Path, gitignore_patterns: list[str]) -> bool:
    """Check if a path should be ignored based on gitignore patterns and common virtual env dirs."""
    # Common virtual environment and build directories to ignore
    ignore_dirs = {
        "venv",
        ".venv",
        "env",
        ".env",
        "virtualenv",
        ".virtualenv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".tox",
        ".nox",
        "dist",
        "build",
        ".git",
        ".svn",
        ".hg",
        ".bzr",
        "site-packages",
        ".mypy_cache",
        ".coverage",
        "htmlcov",
    }

    relative_path = path.relative_to(root_path)
    path_parts = relative_path.parts

    # Check if any part of the path matches ignored directories
    for part in path_parts:
        if part in ignore_dirs:
            return True

    # Check against gitignore patterns
    relative_str = str(relative_path)
    for orig_pattern in gitignore_patterns:
        pattern = orig_pattern
        # Handle directory patterns (ending with /)
        if pattern.endswith("/"):
            pattern = pattern[:-1]
            if fnmatch.fnmatch(relative_str, pattern) or any(fnmatch.fnmatch(part, pattern) for part in path_parts):
                return True
        else:
            # Handle file and directory patterns
            if fnmatch.fnmatch(relative_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
            # Also check if any parent directory matches the pattern
            for i, _part in enumerate(path_parts[:-1]):
                parent_path = "/".join(path_parts[: i + 1])
                if fnmatch.fnmatch(parent_path, pattern):
                    return True

    return False


def get_detected_files(path: str) -> list[Path]:
    """获取递归模式下检测到的所有版本文件。"""
    current_path = Path(path).resolve()
    filenames = ["package.json", "pyproject.toml", "setup.py", "Cargo.toml", "VERSION", "VERSION.txt", "build.gradle.kts"]
    detected_files: list[Path] = []

    # Parse gitignore patterns
    gitignore_patterns = _parse_gitignore(current_path / ".gitignore")

    for root, dirs, files in os.walk(current_path):
        root_path = Path(root)

        # Filter out ignored directories to prevent descending into them
        dirs_to_remove = []
        for dir_name in dirs:
            dir_path = root_path / dir_name
            if _should_ignore_path(dir_path, current_path, gitignore_patterns):
                dirs_to_remove.append(dir_name)

        for dir_name in dirs_to_remove:
            dirs.remove(dir_name)

        # Check files
        for file in files:
            if file in filenames:
                file_path = root_path / file
                if not _should_ignore_path(file_path, current_path, gitignore_patterns):
                    detected_files.append(file_path)

    return detected_files


def get_root_detected_files(path: str) -> list[Path]:
    """获取根目录下检测到的所有版本文件。"""
    current_path = Path(path).resolve()
    filenames = ["package.json", "pyproject.toml", "setup.py", "Cargo.toml", "VERSION", "VERSION.txt", "build.gradle.kts"]
    detected_files: list[Path] = []

    for filename in filenames:
        file_path = current_path / filename
        if file_path.exists():
            detected_files.append(file_path)

    return detected_files


def handle_version(args: VersionArgs) -> None:
    verbose = args.verbose
    path = args.path
    prev_version = get_current_version(path, verbose)
    reclusive = args.recursive

    # 在版本选择前显示检测到的文件
    detected_files = get_detected_files(path) if reclusive else get_root_detected_files(path)

    if detected_files:
        console.print(f"Detected [cyan bold]{len(detected_files)}[/cyan bold] files to update:")
        current_path = Path(path).resolve()
        for file_path in detected_files:
            relative_path = file_path.relative_to(current_path)
            console.print(f"  - {relative_path}")
    else:
        console.print("No version files detected for update.")
        return

    if next_version := get_next_version(args, prev_version, verbose):
        # 获取目标 tag 名
        target_tag = f"v{next_version}"
        # 询问是否生成 changelog
        ans = questionary.confirm(
            f"should generate changelog for {target_tag}?",
            default=True,
        ).ask()
        if ans:
            # 构造 changelog 参数对象

            changelog_args = Namespace(
                path=path,
                from_raw=None,
                to_raw=None,
                output="CHANGELOG.md",
                verbose=verbose,
            )

            # Type ignore needed for argparse Namespace to ChangelogArgs conversion
            handle_changelog(changelog_args, current_tag=target_tag)  # type: ignore[arg-type]
        update_version_files(args, next_version, verbose, reclusive=reclusive)
        execute_git_commands(args, next_version, verbose)


def get_current_version(path: str, verbose: int) -> Version:
    if verbose > 0:
        console.print("Bumping version...")
        console.print("Getting current version...")
    with console.status("[bold green]Getting current version..."):
        prev_version = get_prev_version(path)

    console.print(f"Previous version: [cyan bold]{prev_version}")
    return prev_version


def get_next_version(args: VersionArgs, prev_version: Version | None, verbose: int) -> Version | None:
    if prev_version is None:
        prev_version = Version(major=0, minor=0, patch=0)

    if _has_explicit_version_args(args):
        return _handle_explicit_version_args(args, prev_version)

    default_bump = _get_default_bump_from_commits(args.path, prev_version, verbose)
    return _handle_interactive_version_selection(prev_version, default_bump, verbose)


def _get_default_bump_from_commits(path: str, prev_version: Version, verbose: int) -> str:
    repo = git.Repo(path)
    if verbose > 0:
        console.print("Getting commits...")
    from_ref, to_ref = get_git_commits_range(repo, "", "")
    tgit_commits = get_commits(repo, from_ref, to_ref)
    commits_by_type = group_commits_by_type(tgit_commits)
    # Type ignore needed for TGITCommit to Commit conversion
    return get_default_bump_by_commits_dict(commits_by_type, prev_version)  # type: ignore[arg-type]


def _has_explicit_version_args(args: VersionArgs) -> bool:
    return any([args.custom, args.patch, args.minor, args.major, args.prepatch, args.preminor, args.premajor])


def _handle_explicit_version_args(args: VersionArgs, prev_version: Version) -> Version | None:
    next_version = deepcopy(prev_version)

    if args.patch:
        next_version.patch += 1
    elif args.minor:
        next_version.minor += 1
        next_version.patch = 0
    elif args.major:
        next_version.major += 1
        next_version.minor = 0
        next_version.patch = 0
    elif args.prepatch:
        next_version.patch += 1
        next_version.release = args.prepatch
    elif args.preminor:
        next_version.minor += 1
        next_version.patch = 0
        next_version.release = args.preminor
    elif args.premajor:
        next_version.major += 1
        next_version.minor = 0
        next_version.patch = 0
        next_version.release = args.premajor
    elif args.custom:
        return get_custom_version()

    return next_version


def _handle_interactive_version_selection(prev_version: Version, default_bump: str, verbose: int) -> Version | None:
    bump_options = ["patch", "minor", "major", "prepatch", "preminor", "premajor"]

    # Add "release" option if current version is a prerelease
    if prev_version.release:
        bump_options.insert(0, "release")  # Put it at the beginning for prominence

    bump_options.extend(["previous", "custom"])

    choices = [VersionChoice(prev_version, bump) for bump in bump_options]
    default_choice = next((choice for choice in choices if choice.bump == default_bump), None)

    console.print(f"Auto bump based on commits: [cyan bold]{default_bump}")

    target = _prompt_for_version_choice(choices, default_choice)
    if not target:
        return None

    if verbose > 0:
        console.print(f"Selected target: [cyan bold]{target}")

    return _apply_version_choice(target, prev_version)


def _prompt_for_version_choice(choices: list[VersionChoice], default_choice: VersionChoice | None) -> VersionChoice | None:
    q_choices = [Choice(title=str(choice), value=choice) for choice in choices]
    # Find the corresponding Choice object for default_choice
    default_val = next((c for c in q_choices if c.value == default_choice), None) if default_choice is not None else None

    target = questionary.select(
        "Select the version to bump to",
        choices=q_choices,
        default=default_val,
    ).ask()

    if target is None:
        return None

    if not isinstance(target, VersionChoice):
        msg = "Expected VersionChoice, got different type"
        raise TypeError(msg)

    return target


def _apply_version_choice(target: VersionChoice, prev_version: Version) -> Version | None:
    next_version = deepcopy(prev_version)

    if target.bump in ["prepatch", "preminor", "premajor"]:
        bump_version(target, next_version)
        if release := get_pre_release_identifier():
            next_version.release = release
        else:
            return None
    elif target.bump == "custom":
        if custom_version := get_custom_version():
            next_version = custom_version
        else:
            return None
    elif target.bump == "release":
        # Remove prerelease suffix - next_version is already set correctly in VersionChoice
        next_version = target.next_version
    else:
        # For regular bumps: patch, minor, major, previous
        bump_version(target, next_version)

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
    return questionary.text(
        "Enter the pre-release identifier",
        default="alpha",
        validate=lambda x: bool((match := re.match(r"[0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*", x)) and match.group() == x),  # type: ignore
    ).ask()


def get_custom_version() -> Version | None:
    def validate_semver(x: str) -> bool:
        res = semver_regex.match(x)
        return bool(res and res.group() == x)

    ans = questionary.text(
        "Enter the version",
        validate=validate_semver,
    ).ask()
    if not ans:
        return None
    return Version.from_str(ans)


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

    # 获取检测到的文件列表
    detected_files = get_detected_files(args.path) if reclusive else get_root_detected_files(args.path)

    # 更新文件
    for file_path in detected_files:
        # Check if we're in a test environment to avoid interactive prompts
        is_test_env = "pytest" in sys.modules or "unittest" in sys.modules
        show_diff = not is_test_env and not reclusive
        update_version_in_file(verbose, next_version_str, file_path.name, file_path, show_diff=show_diff)


def update_version_in_file(verbose: int, next_version_str: str, file: str, file_path: Path, *, show_diff: bool = False) -> None:
    # sourcery skip: collection-into-set, merge-duplicate-blocks, remove-redundant-if
    if file == "package.json":
        update_file(str(file_path), r'"version":\s*".*?"', f'"version": "{next_version_str}"', verbose, show_diff=show_diff)
    elif file in ("pyproject.toml", "build.gradle.kts"):
        update_file(str(file_path), r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose, show_diff=show_diff)
    elif file == "setup.py":
        update_file(str(file_path), r"version=['\"].*?['\"]", f"version='{next_version_str}'", verbose, show_diff=show_diff)
    elif file == "Cargo.toml":
        update_cargo_toml_version(str(file_path), next_version_str, verbose, show_diff=show_diff)
    elif file in ("VERSION", "VERSION.txt"):
        update_file(str(file_path), None, next_version_str, verbose, show_diff=show_diff)


def update_file_in_root(next_version_str: str, verbose: int, root_path: Path, *, show_diff: bool = True) -> None:
    update_file(str(root_path / "package.json"), r'"version":\s*".*?"', f'"version": "{next_version_str}"', verbose, show_diff=show_diff)
    update_file(str(root_path / "pyproject.toml"), r'version\s*=\s*".*?"', f'version = "{next_version_str}"', verbose, show_diff=show_diff)
    update_file(str(root_path / "setup.py"), r"version=['\"].*?['\"]", f"version='{next_version_str}'", verbose, show_diff=show_diff)
    update_cargo_toml_version(str(root_path / "Cargo.toml"), next_version_str, verbose, show_diff=show_diff)
    update_file(
        str(root_path / "build.gradle.kts"),
        r'version\s*=\s*".*?"',
        f'version = "{next_version_str}"',
        verbose,
        show_diff=show_diff,
    )
    update_file(str(root_path / "VERSION"), None, next_version_str, verbose, show_diff=show_diff)
    update_file(str(root_path / "VERSION.txt"), None, next_version_str, verbose, show_diff=show_diff)


def update_file(filename: str, search_pattern: str | None, replace_text: str, verbose: int, *, show_diff: bool = True) -> None:
    file_path = Path(filename)
    if not file_path.exists():
        return
    if verbose > 0:
        console.print(f"Updating {file_path}")
    with file_path.open() as f:
        content = f.read()
    new_content = re.sub(search_pattern, replace_text, content) if search_pattern else replace_text
    if show_diff:
        show_file_diff(content, new_content, str(file_path))
    with file_path.open("w") as f:
        f.write(new_content)


def update_cargo_toml_version(filename: str, next_version_str: str, verbose: int, *, show_diff: bool = True) -> None:
    """Update version in Cargo.toml, specifically in the [package] section only."""
    file_path = Path(filename)
    if not file_path.exists():
        return
    if verbose > 0:
        console.print(f"Updating {file_path}")

    with file_path.open() as f:
        content = f.read()

    # Use regex to match version in [package] section only
    # This pattern matches:
    # 1. [package] section header
    # 2. Any content until version = "..."
    # 3. Captures the version line to replace
    pattern = r'(\[package\].*?)(version\s*=\s*"[^"]*")'

    def replace_version(match: re.Match[str]) -> str:
        package_section = match.group(1)
        return f'{package_section}version = "{next_version_str}"'

    new_content = re.sub(pattern, replace_version, content, flags=re.DOTALL)

    if show_diff:
        show_file_diff(content, new_content, str(file_path))

    with file_path.open("w") as f:
        f.write(new_content)


def show_file_diff(old_content: str, new_content: str, filename: str) -> None:
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    diff = list[str](Differ().compare(old_lines, new_lines))
    print_lines = extract_context_lines(diff)

    diffs: list[str] = []
    format_diff_lines(diff, print_lines, diffs)
    if diffs:
        console.print()
        console.print(f"[cyan]Diff for {filename}:[/cyan]")
        console.print("\n".join(diffs))
        ok = questionary.confirm("Do you want to continue?", default=True).ask()
        if not ok:
            sys.exit()


def extract_context_lines(diff: list[str]) -> dict[int, str]:
    print_lines: dict[int, str] = {}
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

    commands: list[str] = []
    if args.no_commit:
        if verbose > 0:
            console.print("Skipping commit")
    else:
        commands.append("git add .")
        use_emoji = settings.commit.emoji
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
    run_command(settings, commands_str)


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("-v", "--verbose", count=True, help="increase output verbosity")
@click.option("--no-commit", is_flag=True, help="do not commit the changes")
@click.option("--no-tag", is_flag=True, help="do not create a tag")
@click.option("--no-push", is_flag=True, help="do not push the changes")
@click.option("-r", "--recursive", is_flag=True, help="bump all packages in the monorepo")
@click.option("-p", "--patch", is_flag=True, help="patch version")
@click.option("-m", "--minor", is_flag=True, help="minor version")
@click.option("-M", "--major", is_flag=True, help="major version")
@click.option("-pp", "--prepatch", help="prepatch version")
@click.option("-pm", "--preminor", help="preminor version")
@click.option("-pM", "--premajor", help="premajor version")
@click.option("--custom", is_flag=True, help="custom version to bump to")
def version(  # noqa: PLR0913
    *,
    path: str,
    verbose: int,
    no_commit: bool,
    no_tag: bool,
    no_push: bool,
    recursive: bool,
    patch: bool,
    minor: bool,
    major: bool,
    custom: bool,
    prepatch: str = "",
    preminor: str = "",
    premajor: str = "",
) -> None:
    # Check for mutually exclusive options
    exclusive_options: list[bool | str] = [patch, minor, major, prepatch, preminor, premajor, custom]
    if sum(bool(opt) for opt in exclusive_options) > 1:
        click.echo("Error: Only one version bump option can be specified at a time.")
        raise click.Abort

    args = VersionArgs(
        version="",  # This will be determined later
        verbose=verbose,
        no_commit=no_commit,
        no_tag=no_tag,
        no_push=no_push,
        patch=patch,
        minor=minor,
        major=major,
        prepatch=prepatch,
        preminor=preminor,
        premajor=premajor,
        recursive=recursive,
        custom="" if not custom else "custom",
        path=path,
    )
    handle_version(args)
