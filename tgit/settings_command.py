"""Settings command for TGIT CLI."""

from .interactive_settings import interactive_settings


def settings() -> None:
    """Interactive settings configuration."""
    interactive_settings()
