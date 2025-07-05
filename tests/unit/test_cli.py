import argparse
from unittest.mock import MagicMock, patch

from tgit.cli import handle, main


class TestCLI:
    def test_handle_with_func(self) -> None:
        """测试当args有func属性时的处理"""
        parser = argparse.ArgumentParser()
        args = argparse.Namespace()
        mock_func = MagicMock()
        args.func = mock_func

        handle(parser, args)

        mock_func.assert_called_once_with(args)

    def test_handle_with_version(self) -> None:
        """测试显示版本信息"""
        parser = argparse.ArgumentParser()
        args = argparse.Namespace()
        args.version = True

        with patch("tgit.cli.importlib.metadata.version", return_value="1.0.0"), patch("tgit.cli.console.print") as mock_print:
            handle(parser, args)
            mock_print.assert_called_once_with("TGIT - ver.1.0.0", highlight=False)

    def test_handle_with_help(self) -> None:
        """测试显示帮助信息"""
        parser = MagicMock()
        args = argparse.Namespace()
        args.version = False

        handle(parser, args)

        parser.print_help.assert_called_once()

    @patch("tgit.cli.handle")
    @patch("tgit.cli.argparse.ArgumentParser.parse_args")
    def test_main_calls_handle(self, mock_parse_args: MagicMock, mock_handle: MagicMock) -> None:
        """测试main函数调用handle"""
        mock_args = MagicMock()
        mock_parse_args.return_value = mock_args

        main()

        mock_handle.assert_called_once()

    @patch("tgit.cli.threading.Thread")
    @patch("tgit.cli.handle")
    @patch("tgit.cli.argparse.ArgumentParser.parse_args")
    def test_main_starts_openai_import_thread(self, mock_parse_args, mock_handle, mock_thread) -> None:
        """测试main函数启动OpenAI导入线程"""
        mock_args = MagicMock()
        mock_parse_args.return_value = mock_args
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        main()

        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    def test_handle_without_func_and_version_false(self) -> None:
        """测试当没有func属性且version为False时显示帮助"""
        parser = MagicMock()
        args = argparse.Namespace()
        args.version = False

        handle(parser, args)

        parser.print_help.assert_called_once()
