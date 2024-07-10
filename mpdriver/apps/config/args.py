# Copyright 2024 The MPDriver3 Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
from typing import Any
from ...core.args_base import subparsers, help_action, textwrap, argparse, NArgsAction, AppArgs, HelpFormatter

command = Path(__file__).parent.name
parser = subparsers.add_parser(command, add_help=False, formatter_class=HelpFormatter)
parser.set_defaults(command=command)
parser._add_action(help_action)

"""
    mpdriver config [--local] [--global] [--system] key [value]
"""

class ConfigArgs(AppArgs):
    command = command
    'コマンド名'
    file_local: bool = parser.add_argument('--local', action=argparse._StoreTrueAction, dest='file_local')
    file_global: bool = parser.add_argument('--global', action=argparse._StoreTrueAction, dest='file_global')
    file_system: bool = parser.add_argument('--system', action=argparse._StoreTrueAction, dest='file_system')
    file_default: bool = parser.add_argument('--default', action=argparse._StoreTrueAction, dest='file_default')
    key: str = parser.add_argument('key', help="項目")
    '項目'
    value: str | None = parser.add_argument('value', nargs=argparse.OPTIONAL, default=None, help="値")
    '値'
    verbose: bool = parser.add_argument('-v', '--verbose', action=argparse._StoreTrueAction)
    yes: bool = parser.add_argument('-y', '--yes', action=argparse._StoreTrueAction)
    # belows is NotImplemented
    copy: str = parser.add_argument('--reset', action=argparse._StoreConstAction, const='default', dest='copy')
    copy: str = parser.add_argument('-c', '--copy')
    copy: str = parser.add_argument('-d', '--delite')
