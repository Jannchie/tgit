"""Type definitions for TGIT."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import argparse

    SubParsersAction = argparse._SubParsersAction[argparse.ArgumentParser]  # type: ignore # noqa: SLF001
else:
    SubParsersAction = Any

# Common settings type
Settings = dict[str, Any]


@dataclass
class CommitType:
    type: str
    emoji: str


@dataclass
class CommitSettings:
    emoji: bool = False
    types: list[CommitType] = field(default_factory=list[CommitType])


@dataclass
class TGitSettings:
    commit: CommitSettings = field(default_factory=CommitSettings)
    api_key: str = ""
    api_url: str = ""
    model: str = ""
    show_command: bool = True
    skip_confirm: bool = False
