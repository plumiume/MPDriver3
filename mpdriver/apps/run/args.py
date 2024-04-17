from pathlib import Path
from typing import TypedDict
import json

from ...core.args_base import subparsers, help_action, textwrap, argparse, NArgsAction, AppArgs, HelpFormatter

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
    annotated: tuple[tuple[Path | None, str], AnnotatedOptions] = parser.add_argument(
        '--annotated', '-a',
        type=((Path, None), {'show': lambda x: bool(json.loads(x)), 'overwrite': lambda x: bool(json.loads(x)), 'fps': float}),
        default=((None, '.mp4'), {'show': False, 'overwrite': False, 'fps': 30}),
        action=NArgsAction, nargs='*',
        help=textwrap.dedent('''
            アノテーション出力
            --annotated dst [ext] [optkey=optvalue]
            positions:
                    dst         アノテーション出力ディレクトリ
                    ext         アノテーション出力の拡張子
            options:
                    show        表示する
                    overwrite   上書きする
                    fps         出力のフレームレート
        ''').strip()
    )
    'アノテーション出力ディレクトリ'
    class LandmarksOptions(TypedDict):
        overwrite: bool
        normalize: bool
        clip: bool
    landmarks: tuple[tuple[Path | None, str], LandmarksOptions] = parser.add_argument(
        '--landmarks', '-l', action=NArgsAction, nargs='*',
        type=((Path, None), {'overwrite': lambda x: bool(json.loads(x)), 'normalize': bool, 'clip': bool}),
        default = (default := ((None, '.csv'), {'overwrite': False, 'normalize': True, 'clip': True})),
        help=textwrap.dedent('''
            ランドマーク出力
            --landmarks dst [ext] [optkey=optvalue]
            requires:
                    dst         ランドマーク出力ディレクトリ
                    ext         ランドマーク出力の拡張子
            options:
                    overwrite   上書きする
                    normalize   正規化する
                    clip        値を -1 ~ 1 の範囲にする
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


