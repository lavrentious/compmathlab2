import argparse
import sys
from argparse import Namespace
from io import TextIOWrapper
from typing import Any

from logger import Logger


class ArgParser:
    parser: argparse.ArgumentParser
    in_stream: None | TextIOWrapper | Any = sys.stdin
    out_stream: None | TextIOWrapper | Any = sys.stdout
    args: Namespace

    # args
    help_mode: bool = False  # help mode
    verbose: bool

    def _register_args(self) -> None:
        self.parser.add_argument("-h", "--help", action="store_true", help="shows help")
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="set verbose mode",
        )

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(add_help=False)
        self._register_args()

    def parse_and_validate_args(self, logger: Logger | None = None) -> int:
        self.args = self.parser.parse_args()

        # if self.args.input_file is not None:
        #     self.in_stream = self.args.input_file
        # if self.args.output_file is not None:
        #     self.out_stream = self.args.output_file

        self.verbose = self.args.verbose or False
        if self.args.help:
            self.help_mode = True

        return 0

    def print_help(self) -> None:
        self.parser.print_help()
