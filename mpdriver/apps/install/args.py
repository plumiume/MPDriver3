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
from ...core.args_base import subparsers, get_help_action, textwrap, argparse, NArgsAction, AppArgs, HelpFormatter

command = Path(__file__).parent.name
parser = subparsers.add_parser(command, add_help=False, formatter_class=HelpFormatter)
parser.set_defaults(command=command)
parser._add_action(get_help_action(
    url='https://github.com/plumiume/MPDriver3/tree/main/mpdriver/apps/install/README.md'
))

"""
    mpdriver install
"""

class InstallArgs(AppArgs):
    command = command
    'コマンド名'
    subcommand = parser.add_argument('subcommand', nargs='?', default=None, choices=['check'])
    'サブコマンド名'
    verbose: bool = parser.add_argument('-v', '--verbose', action=argparse._StoreTrueAction)
    'log level'