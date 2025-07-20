import contextlib
import logging
import re
import warnings
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import click
import git
from markdown_it.token import Token
from rich import print
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markdown import Markdown, MarkdownContext, TextElement
from rich.progress import Progress
from rich.text import Text

from tgit.utils import console

logger = logging.getLogger("tgit")


@dataclass
class VersionSegment:
    """Represents a version segment for changelog generation."""

    from_hash: str
    to_hash: str
    from_name: str
    to_name: str


class Heading(TextElement):
    """A heading."""

    @classmethod
    def create(cls, markdown: Markdown, token: Token) -> "Heading":  # noqa: ARG003
        return cls(token.tag)

    def on_enter(self, context: MarkdownContext) -> None:
        self.text = Text()
        context.enter_style(self.style_name)

    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.style_name = f"markdown.{tag}"
        super().__init__()

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions,
    ) -> RenderResult:
        # 根据标题级别添加相应数量的 # 号
        level = int(self.tag[1])  # 从 h1, h2, h3... 中提取数字
        hash_prefix = "#" * level + " "

        # 创建带有 # 前缀的文本
        prefixed_text = Text(hash_prefix) + Text.from_markup(self.text.plain)
        prefixed_text.justify = None

        if self.tag == "h1":
            # Simple text output for h1s
            yield Text("")
            yield prefixed_text
            yield Text("")
        else:
            # Styled text for h2 and beyond
            if self.tag == "h2":
                yield Text("")
            yield prefixed_text


Markdown.elements["heading_open"] = Heading


def get_latest_git_tag(repo: git.Repo) -> str | None:
    return get_tag_by_idx(repo, -1)


def get_tag_by_idx(repo: git.Repo, idx: int) -> str | None:
    try:
        if tags := sorted(repo.tags, key=lambda t: t.commit.committed_datetime):
            return tags[idx].name
        return None
    except Exception:
        logger.exception("Can't find tag by index %s", idx)
        return None


def get_first_commit_hash(repo: git.Repo) -> str:
    return next(
        (commit.hexsha for commit in repo.iter_commits() if not commit.parents),
        "",
    )


def get_commit_hash_from_tag(repo: git.Repo, tag: str) -> str | None:
    try:
        return repo.tags[tag].commit.hexsha
    except Exception:
        logger.exception("Can't find tag %s", tag)
        return None


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("-f", "--from", "from_raw", help="From hash/tag")
@click.option("-t", "--to", "to_raw", help="To hash/tag")
@click.option("-v", "--verbose", count=True, help="increase output verbosity")
@click.option("-o", "--output", help="output file")
def changelog(
    path: str,
    from_raw: str | None,
    to_raw: str | None,
    verbose: int,
    output: str | None,
) -> None:
    """
    Generate a changelog from git commit history.

    This command analyzes the commit history of a git repository and generates a changelog in markdown format.
    You can specify a range of commits using tags or hashes, or generate changelogs for all unreleased changes.
    The output can be printed to the console or saved to a file.
    """
    # Handle the output parameter like argparse const behavior
    output_value = None if output is None else output or "CHANGELOG.md"

    args = ChangelogArgs(
        path=path,
        from_raw=from_raw,
        to_raw=to_raw,
        verbose=verbose,
        output=output_value,
    )
    handle_changelog(args)


@dataclass
class ChangelogArgs:
    from_raw: str | None
    to_raw: str | None
    verbose: int
    path: str
    output: str | None


def get_simple_hash(repo: git.Repo, git_hash: str, length: int = 7) -> str | None:
    try:
        return repo.git.rev_parse(git_hash, short=length)
    except Exception:
        logger.exception("Can't find hash %s", git_hash)
        return None


def ref_to_hash(repo: git.Repo, ref: str, length: int = 7) -> str | None:
    try:
        return repo.git.rev_parse(ref, short=length)
    except Exception:
        logger.exception("Can't find ref %s", ref)
        return None


commit_pattern = re.compile(
    r"(?P<emoji>:.+:|(\uD83C[\uDF00-\uDFFF])|(\uD83D[\uDC00-\uDE4F\uDE80-\uDEFF])|[\u2600-\u2B55])?( *)?(?P<type>[a-z]+)(\((?P<scope>.+?)\))?(?P<breaking>!)?: (?P<description>.+)",  # noqa: E501
    re.IGNORECASE,
)


def resolve_from_ref(repo: git.Repo, from_raw: str | None) -> str:
    if from_raw is not None and from_raw:
        return from_raw
    last_tag = get_latest_git_tag(repo)
    if last_tag is None:
        return get_first_commit_hash(repo)
    return last_tag


@dataclass
class Author:
    name: str
    email: str

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


class TGITCommit:
    def __init__(self, repo: git.Repo, commit: git.Commit, message_dict: dict[str, str]) -> None:
        commit_date = commit.committed_datetime

        message = commit.message
        if isinstance(message, bytes):
            message = message.decode()
        elif not isinstance(message, str):
            message = str(message)
        co_author_raws = [line for line in message.split("\n") if line.lower().startswith("co-authored-by:")]
        co_author_pattern = re.compile(r"Co-authored-by: (?P<name>.+?) <(?P<email>.+?)>", re.IGNORECASE)
        co_authors = [match.groupdict() for co_author in co_author_raws if (match := co_author_pattern.match(co_author))]
        authors = [{"name": commit.author.name, "email": commit.author.email}, *co_authors]
        self.authors: list[Author] = [Author(**kwargs) for kwargs in authors]
        self.date = commit_date
        self.emoji = message_dict.get("emoji")
        self.type = message_dict.get("type")
        self.scope = message_dict.get("scope")
        self.description = message_dict.get("description")
        self.breaking = bool(message_dict.get("breaking"))
        self.hash = repo.git.rev_parse(commit.hexsha, short=7)

    def __str__(self) -> str:
        authors_str = ", ".join(str(author) for author in self.authors)
        date_str = self.date.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"Hash: {self.hash}\n"
            f"Breaking: {self.breaking}\n"
            f"Commit: {self.emoji or ''} {self.type or ''}{f'({self.scope})' if self.scope else ''}: {self.description}\n"
            f"Date: {date_str}\n"
            f"Authors: {authors_str}\n"
        )


def format_names(names: list[str]) -> str:
    if not names:
        return ""

    if len(names) == 1:
        return f"By {names[0]}"

    if len(names) == 2:  # noqa: PLR2004
        return f"By {names[0]} and {names[1]}"

    formatted_names = ", ".join(names[:-1])
    formatted_names += f" and {names[-1]}"

    return f"By {formatted_names}"


def get_remote_uri(url: str) -> str | None:
    # SSH URL regex, with groups for domain, namespace and repo name
    ssh_pattern = re.compile(r"git@([\w\.]+):(.+)/(.+)\.git")
    # HTTPS URL regex, with groups for domain, namespace and repo name
    https_pattern = re.compile(r"https://([\w\.]+)/(.+)/(.+)\.git")

    if ssh_match := ssh_pattern.match(url):
        domain, namespace, repo_name = ssh_match[1], ssh_match[2], ssh_match[3]
        return f"{domain}/{namespace}/{repo_name}"  # "domain/namespace/repo_name"

    if https_match := https_pattern.match(url):
        domain, namespace, repo_name = https_match[1], https_match[2], https_match[3]
        return f"{domain}/{namespace}/{repo_name}"  # "domain/namespace/repo_name"

    return None


def get_commits(repo: git.Repo, from_hash: str, to_hash: str) -> list[TGITCommit]:
    raw_commits = list(repo.iter_commits(f"{from_hash}...{to_hash}"))
    tgit_commits = []
    for commit in raw_commits:
        message = commit.message
        if isinstance(message, bytes):
            message = message.decode()
        elif not isinstance(message, str):
            message = str(message)
        if m := commit_pattern.match(message):
            message_dict = m.groupdict()
            tgit_commits.append(TGITCommit(repo, commit, message_dict))
    return tgit_commits


def group_commits_by_type(commits: list[TGITCommit]) -> dict[str, list[TGITCommit]]:
    commits_by_type = defaultdict[str, list[TGITCommit]](list[TGITCommit])
    for commit in commits:
        if commit.breaking:
            commits_by_type["breaking"].append(commit)
        elif commit.type:
            commits_by_type[commit.type].append(commit)
    return commits_by_type


def generate_changelog(commits_by_type: dict[str, list[TGITCommit]], from_ref: str, to_ref: str, remote_uri: str | None = None) -> str:
    order = ["breaking", "feat", "fix", "refactor", "perf", "style", "docs", "chore"]
    names = [
        ":rocket: Breaking Changes",
        ":sparkles: Features",
        ":adhesive_bandage: Fixes",
        ":art: Refactors",
        ":zap: Performance Improvements",
        ":lipstick: Styles",
        ":memo: Documentation",
        ":wrench: Chores",
    ]
    out_str = ""
    out_str = f"## {to_ref}\n\n"
    if remote_uri:
        out_str += f"[{from_ref}...{to_ref}](https://{remote_uri}/compare/{from_ref}...{to_ref})\n\n"
    else:
        out_str += f"{from_ref}...{to_ref}\n\n"

    def get_hash_link(commit: TGITCommit) -> str:
        if remote_uri:
            return f"[{commit.hash}](https://{remote_uri}/commit/{commit.hash})"
        return commit.hash

    for i, o in enumerate(order):
        if commits := commits_by_type.get(o):
            title = f"### {names[i]}\n\n"
            out_str += title
            # Sort commits by scope, if scope is None, put it to last
            commits.sort(key=lambda c: c.scope or "zzzzz")
            for commit in commits:
                authors_str = format_names([f"[{a.name}](mailto:{a.email})" for a in commit.authors])
                if commit.scope:
                    line = f"- **{commit.scope}**: {commit.description} - {authors_str} in {get_hash_link(commit)}\n"
                else:
                    line = f"- {commit.description} - {authors_str} in {get_hash_link(commit)}\n"
                out_str += line
            out_str += "\n"
    return out_str


def extract_latest_tag_from_changelog(filepath: str) -> str | None:
    filepath_obj = Path(filepath)
    with contextlib.suppress(FileNotFoundError), filepath_obj.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                return line.strip().removeprefix("## ").strip()
    return None


def prepare_changelog_segments(
    repo: git.Repo,
    latest_tag_in_file: str | None = None,
    current_tag: str | None = None,
) -> list[VersionSegment]:
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    if not tags:
        print("[yellow]No tags found in the repository.[/yellow]")
        return []
    first_commit = get_first_commit_hash(repo)

    points = [first_commit] + [tag.commit.hexsha for tag in tags]
    point_names = [first_commit] + [tag.name for tag in tags]
    if current_tag is not None:
        point_names += ["HEAD"]
        points += ["HEAD"]
    start_idx = 1
    if latest_tag_in_file and latest_tag_in_file in point_names:
        idx = point_names.index(latest_tag_in_file)
        start_idx = idx + 1
    # Create version segments by iterating through version ranges in reverse order
    version_segments: list[VersionSegment] = []
    for i in reversed(range(start_idx, len(points))):
        segment = VersionSegment(
            from_hash=points[i - 1],
            to_hash=points[i],
            from_name=point_names[i - 1],
            to_name=point_names[i],
        )
        version_segments.append(segment)
    if current_tag is not None and version_segments:
        # Update the first segment to use HEAD as the to_hash and current_tag as to_name
        first_segment = version_segments[0]
        version_segments[0] = VersionSegment(
            from_hash=first_segment.from_hash,
            to_hash="HEAD",
            from_name=first_segment.from_name,
            to_name=current_tag,
        )
    return version_segments


def write_changelog_prepend(filepath: str, new_content: str) -> None:
    path = Path(filepath)
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            old_content = f.read()
        with path.open("w", encoding="utf-8") as f:
            f.write(new_content.strip("\n") + "\n\n" + old_content)
    else:
        with path.open("w", encoding="utf-8") as f:
            f.write(new_content.strip("\n") + "\n")


def print_and_write_changelog(
    changelog: str,
    output_path: str | None = None,
    *,
    prepend: bool = False,
) -> None:
    if not changelog or not changelog.strip():
        print("[yellow]No changes found, nothing to output.[/yellow]")
        return
    print()
    console.print("[cyan]Changelog:[/cyan]")
    if output_path:
        console.print(f"[dim]It is saved to {output_path}[/dim]")
    print()
    # rich.Markdown 默认标题居中，需用 console.print 并设置参数 style 和 width
    md = Markdown(changelog.strip("\n"), justify="left")
    console.print(md)
    if output_path:
        if prepend:
            write_changelog_prepend(output_path, changelog)
        else:
            with Path(output_path).open("w", encoding="utf-8") as output_file:
                output_file.write(changelog.strip("\n") + "\n")


def handle_changelog(args: ChangelogArgs, current_tag: str | None = None) -> None:
    repo = git.Repo(args.path)
    from_raw = args.from_raw
    to_raw = args.to_raw
    latest_tag_in_file = None

    if args.output and Path(args.output).exists() and from_raw is None and to_raw is None:
        latest_tag_in_file = extract_latest_tag_from_changelog(args.output)

    # 根据参数获取对应的分段
    if from_raw is not None or to_raw is not None:
        segments = _get_range_segments(repo, from_raw, to_raw)
        prepend = False
    else:
        segments = prepare_changelog_segments(repo, latest_tag_in_file, current_tag)
        prepend = bool(latest_tag_in_file)

    # 检查是否有新的更改需要生成 changelog
    if not segments:
        if latest_tag_in_file:
            # 检查文件中的最新 tag 是否已经是仓库中的最新 tag
            latest_repo_tag = get_latest_git_tag(repo)
            if latest_tag_in_file == latest_repo_tag:
                print("[green]Changelog is already up to date.[/green]")
                return
        else:
            print("[yellow]No changes found, nothing to output.[/yellow]")
            return

    # 生成 changelog
    changelogs = _generate_changelogs_from_segments(repo, segments)

    # 输出结果
    print_and_write_changelog(changelogs, args.output, prepend=prepend)


def _get_range_segments(repo: git.Repo, from_raw: str | None, to_raw: str | None) -> list[VersionSegment]:
    """获取指定范围的分段"""
    from_ref, to_ref = get_git_commits_range(repo, from_raw or "", to_raw or "")
    segments = prepare_changelog_segments(repo)

    # 找到 from_ref 和 to_ref 在分段中的索引
    start, end = 0, len(segments)
    for i, seg in enumerate(segments):
        # 匹配 tag 名或 hash
        if from_ref in (seg.from_name, seg.from_hash):
            start = i
        if to_ref in (seg.to_name, seg.to_hash):
            end = i + 1

    return segments[start:end]


def _generate_changelogs_from_segments(repo: git.Repo, segments: list[VersionSegment]) -> str:
    """从分段列表生成 changelog"""
    if not segments:
        return ""

    changelogs = ""

    with Progress() as progress:
        task = progress.add_task("Generating changelog...", total=len(segments))

        for segment in segments:
            from_hash, to_hash, from_name, to_name = segment.from_hash, segment.to_hash, segment.from_name, segment.to_name
            # 获取提交信息
            raw_commits = list(repo.iter_commits(f"{from_hash}...{to_hash}"))
            tgit_commits = _process_commits(repo, raw_commits)
            commits_by_type = group_commits_by_type(tgit_commits)

            # 获取远程仓库信息
            remote_uri = _get_remote_uri_safe(repo)

            # 生成 changelog
            changelog = generate_changelog(commits_by_type, from_name, to_name, remote_uri)
            changelogs += changelog

            progress.update(task, advance=1)

    return changelogs


def _process_commits(repo: git.Repo, raw_commits: list) -> list:
    """处理原始提交，转换为 TGITCommit 对象"""
    tgit_commits = []
    for commit in raw_commits:
        message = commit.message.decode() if isinstance(commit.message, bytes) else commit.message
        if m := commit_pattern.match(message):
            message_dict = m.groupdict()
            tgit_commits.append(TGITCommit(repo, commit, message_dict))
    return tgit_commits


def _get_remote_uri_safe(repo: git.Repo) -> str | None:
    """安全地获取远程仓库 URI"""
    try:
        origin_url = repo.remote().url
        return get_remote_uri(origin_url)
    except ValueError:
        return None


def get_changelog_by_range(repo: git.Repo, from_ref: str, to_ref: str) -> str:
    try:
        origin_url = repo.remote().url
        remote_uri = get_remote_uri(origin_url)
    except ValueError:
        warnings.warn("Origin not found, some of the link generation functions could not be enabled.", stacklevel=2)
        remote_uri = None

    tgit_commits = get_commits(repo, from_ref, to_ref)
    commits_by_type = group_commits_by_type(tgit_commits)
    return generate_changelog(commits_by_type, from_ref, to_ref, remote_uri)


def get_git_commits_range(repo: git.Repo, from_raw: str | None, to_raw: str | None) -> tuple[str, str]:
    from_ref = resolve_from_ref(repo, from_raw if from_raw else None)
    to_ref = to_raw if to_raw else "HEAD"
    return from_ref, to_ref
