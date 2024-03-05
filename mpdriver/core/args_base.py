import argparse
from argparse import Action
import textwrap
from typing import Any, Callable, Iterable, Mapping
from types import ModuleType
from itertools import count

class AppArgs(argparse.Namespace):
    '''サブコマンドのフィールド定義'''
    command: str

class AppMainModule(ModuleType):
    def app_main(self, namespace: AppArgs):
        raise NotImplementedError

class NArgsAction(argparse.Action):

    def __init__(
        self,
        type: tuple[Iterable[Callable[[str], Any] | None], Mapping[str, Callable[[str], Any]| None]] | None = None,
        default: tuple[Iterable[Any], Mapping[str, Any]] = ([], {}),
        **kwargs
        ):

        super().__init__(type=None, default=default, **kwargs)

        self.type_functions = (iter(type[0]), type[1])
        self.type_args_cache = list[Callable[[str], Any]]()
        self.default: tuple[Iterable[Any], Mapping[str, Any]] = default

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | list[str],
        option_strings: list[str]
        ):

        if isinstance(values, str):
            values = [values]

        pos_opt: tuple[tuple[Any], dict[str, Any]] | None = getattr(namespace, self.dest, None)
        if pos_opt is None:
            pos = dict(enumerate(self.default[0]))
            opt = dict(self.default[1])
        else:
            pos = dict(enumerate(pos_opt[0]))
            opt = pos_opt[1]

        type_args_cache_iter = iter(self.type_args_cache)
        type_kwargs_idx = count()

        for v in values:

            if '=' in v[1:]:
                ok, ov = v.split('=')
                opt[ok] = self.type_functions[1][ok](ov)
                continue

            tf = next(type_args_cache_iter, None)
            if tf is None:
                tf = next(self.type_functions[0])
                if tf is None: tf = lambda x: x
                self.type_args_cache.append(tf)
            pos[next(type_kwargs_idx)] = tf(v)

        setattr(namespace, self.dest, (tuple(pos.values()), opt))

class HelpFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):

    def _get_help_string(self, action: Action) -> str | None:
        return super()._get_help_string(action)

    def _format_args(self, action: argparse.Action, default_metavar: str) -> str:
        get_metavar = self._metavar_formatter(action, default_metavar)
        # ADD
        if isinstance(action, NArgsAction):
            result = '*ARGS **KWARGS'
            return result
        # END ADD
        if action.nargs is None:
            result = '%s' % get_metavar(1)
        elif action.nargs == argparse.OPTIONAL:
            result = '[%s]' % get_metavar(1)
        elif action.nargs == argparse.ZERO_OR_MORE:
            metavar = get_metavar(1)
            if len(metavar) == 2:
                result = '[%s [%s ...]]' % metavar
            else:
                result = '[%s ...]' % metavar
        elif action.nargs == argparse.ONE_OR_MORE:
            result = '%s [%s ...]' % get_metavar(2)
        elif action.nargs == argparse.REMAINDER:
            result = '...'
        elif action.nargs == argparse.PARSER:
            result = '%s ...' % get_metavar(1)
        elif action.nargs == argparse.SUPPRESS:
            result = ''
        else:
            try:
                formats = ['%s' for _ in range(action.nargs)]
            except TypeError:
                raise ValueError("invalid nargs value") from None
            result = ' '.join(formats) % get_metavar(action.nargs)
        return result

_root_argparser = argparse.ArgumentParser(
    formatter_class = HelpFormatter,
    prog = 'mpdriver',
    description = 'MediaPipeDriver コマンドライン',
    epilog = textwrap.dedent('''
        各サブコマンドのヘルプも確認できます
            mpdriver <command> -h
    '''),
    add_help = False,
    allow_abbrev=False
)
'''mpdriverのルート引数解析器'''

help_action = _root_argparser.add_argument(
    '--help', '-h',
    action = argparse._HelpAction,
    help = 'このヘルプメッセージを表示して終了する'
)
'''カスタムヘルプメッセージ'''

subparsers = _root_argparser.add_subparsers(
    title = 'sub commands',
    metavar = '<command>',
    required = True
)
