"""Test type definitions for TGIT."""

from typing import Any
import argparse

from tgit.types import SubParsersAction, Settings


class TestSubParsersAction:
    def test_subparsers_action_type_checking_false(self):
        """Test SubParsersAction when TYPE_CHECKING is False"""
        # In runtime, SubParsersAction should be Any
        assert SubParsersAction == Any

    def test_subparsers_action_real_usage(self):
        """Test SubParsersAction with real argparse usage"""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        # This should work with our type alias
        assert isinstance(subparsers, argparse._SubParsersAction)  # noqa: SLF001


class TestSettings:
    def test_settings_type_alias(self):
        """Test Settings type alias"""
        # Settings should be equivalent to dict[str, Any]
        test_settings: Settings = {"key": "value", "number": 42, "bool": True}

        assert isinstance(test_settings, dict)
        assert test_settings["key"] == "value"
        assert test_settings["number"] == 42
        assert test_settings["bool"] is True

    def test_settings_empty(self):
        """Test empty Settings"""
        empty_settings: Settings = {}
        assert isinstance(empty_settings, dict)
        assert len(empty_settings) == 0

    def test_settings_nested(self):
        """Test nested Settings"""
        nested_settings: Settings = {
            "api": {"key": "secret", "url": "https://api.example.com"},
            "commit": {"emoji": True, "types": ["feat", "fix"]},
        }

        assert isinstance(nested_settings, dict)
        assert nested_settings["api"]["key"] == "secret"
        assert nested_settings["commit"]["emoji"] is True
        assert nested_settings["commit"]["types"] == ["feat", "fix"]

    def test_settings_mixed_types(self):
        """Test Settings with various data types"""
        mixed_settings: Settings = {
            "string": "value",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none": None,
        }

        assert isinstance(mixed_settings, dict)
        assert mixed_settings["string"] == "value"
        assert mixed_settings["integer"] == 42
        assert mixed_settings["float"] == 3.14
        assert mixed_settings["boolean"] is True
        assert mixed_settings["list"] == [1, 2, 3]
        assert mixed_settings["dict"]["nested"] == "value"
        assert mixed_settings["none"] is None
