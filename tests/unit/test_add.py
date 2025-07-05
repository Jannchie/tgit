import argparse
from unittest.mock import MagicMock, patch

from tgit.add import define_add_parser, handle_add


class TestAdd:
    def test_define_add_parser(self):
        """测试定义add解析器"""
        subparsers = MagicMock()
        mock_parser = MagicMock()
        subparsers.add_parser.return_value = mock_parser

        define_add_parser(subparsers)

        subparsers.add_parser.assert_called_once_with("add", help="same as git add")
        mock_parser.add_argument.assert_called_once_with("files", help="files to add", nargs="*")
        mock_parser.set_defaults.assert_called_once_with(func=handle_add)

    @patch("tgit.add.simple_run_command")
    def test_handle_add_single_file(self, mock_run_command):
        """测试添加单个文件"""
        args = argparse.Namespace()
        args.files = ["test.py"]

        handle_add(args)

        mock_run_command.assert_called_once_with("git add test.py")

    @patch("tgit.add.simple_run_command")
    def test_handle_add_multiple_files(self, mock_run_command):
        """测试添加多个文件"""
        args = argparse.Namespace()
        args.files = ["test1.py", "test2.py", "test3.py"]

        handle_add(args)

        mock_run_command.assert_called_once_with("git add test1.py test2.py test3.py")

    @patch("tgit.add.simple_run_command")
    def test_handle_add_no_files(self, mock_run_command):
        """测试没有文件时的处理"""
        args = argparse.Namespace()
        args.files = []

        handle_add(args)

        mock_run_command.assert_called_once_with("git add ")

    @patch("tgit.add.simple_run_command")
    def test_handle_add_with_paths_containing_spaces(self, mock_run_command):
        """测试包含空格的文件路径"""
        args = argparse.Namespace()
        args.files = ["file with spaces.py", "another file.txt"]

        handle_add(args)

        mock_run_command.assert_called_once_with("git add file with spaces.py another file.txt")
