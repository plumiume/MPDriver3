from pathlib import Path
from typing import Any
from ...core.args_base import subparsers, help_action, textwrap, argparse, NArgsAction, AppArgs, HelpFormatter

command = Path(__file__).parent.name
parser = subparsers.add_parser(command, add_help=False, formatter_class=HelpFormatter)
parser.set_defaults(command=command)
parser._add_action(help_action)

"""
    mpdriver install
"""

class InstallArgs(AppArgs):
    command = command
    'コマンド名'
    verbose: bool = parser.add_argument('-v', '--verbose', action=argparse._StoreTrueAction)