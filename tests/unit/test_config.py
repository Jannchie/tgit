import argparse
from unittest.mock import MagicMock, patch

from tgit.config import define_config_parser, handle_config


class TestConfig:
    def test_define_config_parser(self):
        """测试定义config解析器"""
        subparsers = MagicMock()
        mock_parser = MagicMock()
        subparsers.add_parser.return_value = mock_parser

        define_config_parser(subparsers)

        subparsers.add_parser.assert_called_once_with("config", help="edit settings")
        assert mock_parser.add_argument.call_count == 2
        mock_parser.add_argument.assert_any_call("key", help="setting key")
        mock_parser.add_argument.assert_any_call("value", help="setting value")
        mock_parser.set_defaults.assert_called_once_with(func=handle_config)

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_handle_config_valid_key(self, mock_print, mock_set_settings):
        """测试处理有效的配置键"""
        args = argparse.Namespace()
        args.key = "apiKey"
        args.value = "test-api-key"

        result = handle_config(args)

        mock_set_settings.assert_called_once_with("apiKey", "test-api-key")
        mock_print.assert_not_called()
        assert result == 0

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_handle_config_all_valid_keys(self, mock_print, mock_set_settings):
        """测试所有有效的配置键"""
        valid_keys = ["apiKey", "apiUrl", "model"]

        for key in valid_keys:
            args = argparse.Namespace()
            args.key = key
            args.value = f"test-{key}"

            result = handle_config(args)

            mock_set_settings.assert_called_with(key, f"test-{key}")
            assert result == 0

        mock_print.assert_not_called()

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_handle_config_invalid_key(self, mock_print, mock_set_settings):
        """测试处理无效的配置键"""
        args = argparse.Namespace()
        args.key = "invalidKey"
        args.value = "test-value"

        result = handle_config(args)

        mock_set_settings.assert_not_called()
        mock_print.assert_called_once_with("Key invalidKey is not valid")
        assert result == 1

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_handle_config_no_key(self, mock_print, mock_set_settings):
        """测试没有提供key的情况"""
        args = argparse.Namespace()
        args.key = None
        args.value = "test-value"

        result = handle_config(args)

        mock_set_settings.assert_not_called()
        mock_print.assert_called_once_with("Key is required")
        assert result == 1

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_handle_config_no_value(self, mock_print, mock_set_settings):
        """测试没有提供value的情况"""
        args = argparse.Namespace()
        args.key = "apiKey"
        args.value = None

        result = handle_config(args)

        mock_set_settings.assert_not_called()
        mock_print.assert_called_once_with("Value is required")
        assert result == 1

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_handle_config_empty_key(self, mock_print, mock_set_settings):
        """测试空key的情况"""
        args = argparse.Namespace()
        args.key = ""
        args.value = "test-value"

        result = handle_config(args)

        mock_set_settings.assert_not_called()
        mock_print.assert_called_once_with("Key is required")
        assert result == 1

    @patch("tgit.config.set_global_settings")
    @patch("tgit.config.print")
    def test_handle_config_empty_value(self, mock_print, mock_set_settings):
        """测试空value的情况"""
        args = argparse.Namespace()
        args.key = "apiKey"
        args.value = ""

        result = handle_config(args)

        mock_set_settings.assert_not_called()
        mock_print.assert_called_once_with("Value is required")
        assert result == 1
