"""Settings command for TGIT CLI."""

import click

from .interactive_settings import interactive_settings


@click.command()
def settings() -> None:
    """Interactive settings configuration."""
    interactive_settings()
