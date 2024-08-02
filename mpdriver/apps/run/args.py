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
from typing import TypedDict
import json

from ...core.args_base import subparsers, help_action, textwrap, argparse, NArgsAction, AppArgs, HelpFormatter, Boolean

command = Path(__file__).parent.name
parser = subparsers.add_parser(command, add_help=False, formatter_class=HelpFormatter)
parser.set_defaults(command=command)
parser._add_action(help_action)

"""
    mpdriver run src -a path/to/ann mp4 -o -l path/to/lm csv -o --show -p 1
    ==> mpdriver [run {src} {annotated_spec} {landmarks_sepc} {processors}]
"""

class RunArgs(AppArgs):
    command = command
    'コマンド名'
    src: Path = parser.add_argument('src', type=Path, help='入力 動画ファイルまたは連続画像ディレクトリ')
    '入力 動画ファイルまたは連続画像ディレクトリ'
    class AnnotatedOptions(TypedDict):
        show: bool
        overwrite: bool
        fps: float
        draw_lm: bool
        draw_conn: bool
        mask_face: bool
    annotated: tuple[tuple[Path | None, str], AnnotatedOptions] = parser.add_argument(
        '--annotated', '-a',
        type=((Path, None), {'show': Boolean, 'overwrite': Boolean, 'fps': float, 'draw_lm': Boolean, 'draw_conn': Boolean, 'mask_face': Boolean}),
        default=((None, '.mp4'), {'show': False, 'overwrite': False, 'fps': 30, 'draw_lm': True, 'draw_conn': True, 'mask_face': True}),
        action=NArgsAction, nargs='*',
        help=textwrap.dedent('''
            アノテーション出力
            --annotated dst [ext] [optkey=optvalue]
            positions:
                    dst         アノテーション出力ディレクトリ
                    ext         アノテーション出力の拡張子
            options:
                    show        表示する (True)
                    overwrite   上書きする (False)
                    fps         出力のフレームレート (30)
                    draw_lm     ランドマークの描画 (True)
                    draw_conn   ボーンの表示 (True)
                    mask_face   顔のマスキング (False)
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
        type=((Path, None), {'overwrite': Boolean, 'normalize': Boolean, 'clip': Boolean, 'header': Boolean}),
        default = ((None, '.csv'), {'overwrite': False, 'normalize': True, 'clip': True, 'header': False}),
        help=textwrap.dedent('''
            ランドマーク出力
            --landmarks dst [ext] [optkey=optvalue]
            requires:
                    dst         ランドマーク出力ディレクトリ
                    ext         ランドマーク出力の拡張子
                                .csv  : CSV
                                .npy  : Numpy.npy
            options:
                    overwrite   上書きする (False)
                    normalize   正規化する (True)
                    clip        値を -1 ~ 1 の範囲にする (True)
                    header      .csvのヘッダをつける (False)
                                ヘッダー行を表す # が先頭に付加されます
                                e.g. '# LM0_X, LM0_Y, LM0_Z, LM1_X, ...'
        ''').strip()
    )
    'ランドマーク出力ディレクトリ'
    cpu: int | None = parser.add_argument(
        '--cpu', '-p', type=int, default=None,
        help='マルチプロセスの数'
    )
    add_ext: list[str] = parser.add_argument(
        '--add-ext', type=str, action=argparse._AppendAction,
        help='入力動画ファイルの追加の拡張子', default=list()
    )
