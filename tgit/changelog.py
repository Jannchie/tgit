import re
import warnings
from collections import defaultdict
from dataclasses import dataclass

import git


def get_latest_git_tag(repo: git.Repo):
    return get_tag_by_idx(repo, -1)


def get_tag_by_idx(repo: git.Repo, idx: int):
    try:
        if tags := sorted(repo.tags, key=lambda t: t.commit.committed_datetime):
            return tags[idx].name
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_first_commit_hash(repo: git.Repo) -> str:
    return next(
        (commit.hexsha for commit in repo.iter_commits() if not commit.parents),
        None,
    )


def get_commit_hash_from_tag(repo: git.Repo, tag):
    try:
        return repo.tags[tag].commit.hexsha
    except Exception as e:
        print(f"Error: {e}")
        return None


def define_changelog_parser(subparsers):
    parser_changelog = subparsers.add_parser("changelog", help="generate changelogs")
    parser_changelog.add_argument("-f", "--from", help="From hash/tag", type=str, dest="from_raw")
    parser_changelog.add_argument("-t", "--to", help="To hash/tag", type=str, dest="to_raw")
    parser_changelog.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity", dest="verbose")
    parser_changelog.add_argument("path", help="repository path", type=str, nargs="?", default=".")
    parser_changelog.set_defaults(func=handle_changelog)


@dataclass
class ChangelogArgs:
    from_raw: str
    to_raw: str
    verbose: int
    path: str


def get_simple_hash(repo: git.Repo, hash, length=7):
    try:
        return repo.git.rev_parse(hash, short=length)
    except Exception as e:
        print(f"Error: {e}")
        return None


def ref_to_hash(repo: git.Repo, ref: str, length=7):
    try:
        return repo.git.rev_parse(ref, short=length)
    except Exception as e:
        print(f"Error: {e}")
        return None


commit_pattern = re.compile(
    r"(?P<emoji>:.+:|(\uD83C[\uDF00-\uDFFF])|(\uD83D[\uDC00-\uDE4F\uDE80-\uDEFF])|[\u2600-\u2B55])?( *)?(?P<type>[a-z]+)(\((?P<scope>.+?)\))?(?P<breaking>!)?: (?P<description>.+)",
    re.IGNORECASE,
)


def resolve_from_ref(repo, from_raw):
    if from_raw is not None:
        return from_raw
    last_tag = get_latest_git_tag(repo)
    return get_first_commit_hash(repo) if last_tag is None else last_tag


@dataclass
class Author:
    name: str
    email: str

    def __str__(self):
        return f"{self.name} <{self.email}>"


class TGITCommit:
    def __init__(self, repo: git.Repo, commit: git.Commit, message_dict: dict):
        commit_date = commit.committed_datetime

        co_author_raws = [line for line in commit.message.split("\n") if line.lower().startswith("co-authored-by:")]
        co_author_pattern = re.compile(r"Co-authored-by: (?P<name>.+?) <(?P<email>.+?)>", re.IGNORECASE)
        co_authors = [co_author_pattern.match(co_author).groupdict() for co_author in co_author_raws]
        authors = [{"name": commit.author.name, "email": commit.author.email}] + co_authors
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


def format_names(names):
    if not names:
        return ""

    if len(names) == 1:
        return f"By {names[0]}"

    if len(names) == 2:
        return f"By {names[0]} and {names[1]}"

    formatted_names = ", ".join(names[:-1])
    formatted_names += f" and {names[-1]}"

    return f"By {formatted_names}"


def get_remote_uri(url: str):
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
        if m := commit_pattern.match(commit.message):
            message_dict = m.groupdict()
            tgit_commits.append(TGITCommit(repo, commit, message_dict))
    return tgit_commits


def group_commits_by_type(commits: list[TGITCommit]) -> dict[str, list[TGITCommit]]:
    commits_by_type = defaultdict(list)
    for commit in commits:
        if commit.breaking:
            commits_by_type["breaking"].append(commit)
        else:
            commits_by_type[commit.type].append(commit)
    return commits_by_type


def generate_changelog(commits_by_type: dict[str, list[TGITCommit]], from_ref: str, to_ref: str, remote_uri: str = None) -> str:
    order = ["breaking", "feat", "fix", "refactor", "perf", "style", "docs", "chore"]
    names = [
        ":rocket: Breaking Changes",
        ":sparkles: Features",
        ":bug: Fixes",
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

    def get_hash_link(commit: TGITCommit):
        if remote_uri:
            return f"[{commit.hash}](https://{remote_uri}/commit/{commit.hash})"
        return commit.hash

    for i, o in enumerate(order):
        if commits := commits_by_type.get(o):
            title = f"### {names[i]}\n\n"
            out_str += title
            # Sort commits by scope, if scope is None, put it to last
            commits.sort(key=lambda c: "zzzzz" if c.scope is None else c.scope)
            for commit in commits:

                authors_str = format_names([f"[{a.name}](mailto:{a.email})" for a in commit.authors])
                if commit.scope:
                    line = f"- **{commit.scope}**: {commit.description} - {authors_str} in {get_hash_link(commit)}\n"
                else:
                    line = f"- {commit.description} - {authors_str} in {get_hash_link(commit)}\n"
                out_str += line
            out_str += "\n"
    return out_str


def handle_changelog(args: ChangelogArgs):
    repo = git.Repo(args.path)
    from_ref = resolve_from_ref(repo, args.from_raw)
    to_ref = "HEAD" if args.to_raw is None else args.to_raw
    if to_ref == "HEAD":
        latest_commit = repo.head.commit
        tags = repo.tags
        latest_commit_tags = [tag for tag in tags if tag.commit == latest_commit]
        if latest_commit_tags:
            to_ref = from_ref
            from_ref = get_tag_by_idx(repo, -2)
            if from_ref is None:
                from_ref = get_first_commit_hash(repo)
        else:
            warnings.warn("HEAD is not a tag, changelog will be generated from the last tag to HEAD.")
    from_hash = ref_to_hash(repo, from_ref)
    to_hash = ref_to_hash(repo, to_ref)

    try:
        origin_url = repo.remote().url
        remote_uri = get_remote_uri(origin_url)
    except ValueError:
        warnings.warn("Origin not found, some of the link generation functions could not be enabled.")
        remote_uri = None

    tgit_commits = get_commits(repo, from_hash, to_hash)
    commits_by_type = group_commits_by_type(tgit_commits)
    changelog = generate_changelog(commits_by_type, from_ref, to_ref, remote_uri)
    print()
    print(changelog)
