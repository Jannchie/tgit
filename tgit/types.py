"""Type definitions for TGIT."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import argparse

    SubParsersAction = argparse._SubParsersAction[argparse.ArgumentParser]  # type: ignore # noqa: SLF001
else:
    SubParsersAction = Any

# Common settings type
Settings = dict[str, Any]
