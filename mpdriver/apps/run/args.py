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
from typing import TypedDict, Any

from ...core.args_base import subparsers, get_help_action, textwrap, argparse, NArgsAction, AppArgs, HelpFormatter, Boolean
from .help import HELP

command = Path(__file__).parent.name
parser = subparsers.add_parser(command, add_help=False, formatter_class=HelpFormatter)
parser.set_defaults(command=command)
parser._add_action(get_help_action(
    url='https://github.com/plumiume/MPDriver3/blob/main/mpdriver/apps/run/README.md'
))
"""
    mpdriver run src -a path/to/ann mp4 -o -l path/to/lm csv -o --show -p 1
    or
    mpdriver run -a path/to/ann mp4 -o -l path/to/lm csv -o --show -p 1 -- src
    ==> mpdriver [run {src} {annotated_spec} {landmarks_sepc} {processors}]
"""

def runarg_config_type(x: str):
    k, v, *_ = x.split('=')
    return k, v

class RunArgs(AppArgs):
    command = command
    'コマンド名'
    src: Path = parser.add_argument('src', type=Path, help=HELP['apps.run.args:src'])
    '入力 動画ファイルまたは連続画像ディレクトリ'
    class AnnotatedOptions(TypedDict):
        show: bool
        overwrite: bool
        fps: float
        draw_lm: bool
        draw_conn: bool
        mask_face: bool
        fourcc: str | None
    annotated: tuple[tuple[Path | None, str], AnnotatedOptions] = parser.add_argument(
        '--annotated', '-a',
        type=(_type:=(
            (Path, None),
            {
                'show': Boolean,'overwrite': Boolean, 'fps': float,
                'draw_lm': Boolean, 'draw_conn': Boolean, 'mask_face': Boolean,
                'fourcc': str
            }
        )),
        default=(_default:=(
            (None, '.mp4'),
            {
                'show': False, 'overwrite': False, 'fps': 30,
                'draw_lm': True, 'draw_conn': True, 'mask_face': True,
                'fourcc': None
            }
        )),
        action=NArgsAction, nargs='*',
        help=textwrap.dedent(f'''
            {HELP['apps.run.args:annotated_options_title']}
            --annotated dst [ext] [optkey=optvalue]
            positions:
                    dst         {HELP['apps.run.args:annotated_options_dst'].format(
                        type=_type[0][0], default=_default[0][0])}
                    ext         {HELP['apps.run.args:annotated_options_ext'].format(
                        type=_type[0][1], default=_default[0][1])}
            options:
                    show        {HELP['apps.run.args:annotated_options_show'].format(
                        type=_type[1]['show'], default=_default[1]['show'])}
                    overwrite   {HELP['apps.run.args:annotated_options_overwirte'].format(
                        type=_type[1]['overwrite'], default=_default[1]['overwrite'])}
                    fps         {HELP['apps.run.args:annotated_options_fps'].format(
                        type=_type[1]['fps'], default=_default[1]['fps'])}
                    draw_lm     {HELP['apps.run.args:annotated_options_draw_lm'].format(
                        type=_type[1]['draw_lm'], default=_default[1]['draw_lm'])}
                    draw_conn   {HELP['apps.run.args:annotated_options_draw_conn'].format(
                        type=_type[1]['draw_conn'], default=_default[1]['draw_conn'])}
                    mask_face   {HELP['apps.run.args:annotated_options_mask_face'].format(
                        type=_type[1]['mask_face'], default=_default[1]['mask_face'])}
                    fourcc      {HELP['apps.run.args.annotated_options_fourcc'].format(
                        type=_type[1]['fourcc'], default=_default[1]['fourcc'])}
                    
        ''').strip()
    )
    'アノテーション出力ディレクトリ'
    class LandmarksOptions(TypedDict):
        overwrite: bool
        normalize: bool
        clip: bool
        header: bool
    landmarks: tuple[tuple[Path | None, str], LandmarksOptions] = parser.add_argument(
        '--landmarks', '-l', action=NArgsAction, nargs='*',
        type=(_type:=(
            (Path, None),
            {'overwrite': Boolean, 'normalize': Boolean, 'clip': Boolean, 'header': Boolean}
        )),
        default=(_default:=(
            (None, '.csv'),
            {'overwrite': False, 'normalize': True, 'clip': True, 'header': False}
        )),
        help=textwrap.dedent(f'''
            {HELP['apps.run.args:landmarks_options_title']}
            --landmarks dst [ext] [optkey=optvalue]
            requires:
                    dst         {HELP['apps.run.args:landmarks_options_dst'].format(
                        type=_type[0][0], default=_default[0][0])}
                    ext         {HELP['apps.run.args:landmarks_options_ext'].format(
                        type=_type[0][1], default=_default[0][1])}
            options:
                    overwrite   {HELP['apps.run.args:landmarks_options_overwrite'].format(
                        type=_type[1]['overwrite'], default=_default[1]['overwrite'])}
                    normalize   {HELP['apps.run.args:landmarks_options_normalize'].format(
                        type=_type[1]['normalize'], default=_default[1]['normalize'])}
                    clip        {HELP['apps.run.args:landmarks_options_clip'].format(
                        type=_type[1]['clip'], default=_default[1]['clip'])}
                    header      {HELP['apps.run.args:landmarks_options_header_0'].format(
                        type=_type[1]['header'], default=_default[1]['header'])}
                                {HELP['apps.run.args:landmarks_options_header_1'].format(
                                    type=_type[1]['header'], default=_default[1]['header'])}
        ''').strip()
    )
    'ランドマーク出力ディレクトリ'
    cpu: int | None = parser.add_argument(
        '--cpu', '-p', type=int, default=None,
        help=HELP['apps.run.args:cpu']
    )
    add_ext: list[str] = parser.add_argument(
        '--add-ext', type=str, action=argparse._AppendAction,
        help=HELP['apps.run.args:add_ext'], default=list()
    )
    config: list[tuple[str, str]] = parser.add_argument(
        '--config', '-c', action=argparse._AppendAction,
        type=runarg_config_type,
        help=HELP['apps.run.args:config'], default=list()
    )
