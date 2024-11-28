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

from typing import Iterable, Literal, Callable, TypeVar, overload, Any
from pathlib import Path
import json

_T = TypeVar('_T')
_U = TypeVar('_U')

_LIBRARY_ROOT = Path(__file__).resolve().parents[1]
CPATH: dict[Literal['local', 'global', 'system'], Path] = { # ORDERD
    'local': Path().resolve() / '.mpdriver',
    'global': Path('~').resolve() / '.mpdriver',
    'system': _LIBRARY_ROOT / 'config/system'
}
DPATH = [
    'config/default',
    'engine/{cfile_stem}'
]

@overload
def _find(func: Callable[[_T], bool], iterable: Iterable[_T]) -> _T: ...
@overload
def _find(func: Callable[[_T], bool], iterable: Iterable[_T], default: _U) -> _T | _U: ...
def _find(func: Callable[[_T], bool], iterable: Iterable[_T], *args: _U):
    for item in iterable:
        if func(item):
            return item
    if args:
        default, *_ = args
        return default
    else:
        raise ValueError

@overload
def load_config(cfile_stem: str, use: Literal['local', 'global', 'system', 'default'] = 'local', default_path: Path | None = None, ctype: None = ...) -> Any: ...
@overload
def load_config(cfile_stem: str, use: Literal['local', 'global', 'system', 'default'] = 'local', default_path: Path | None = None, ctype: type[_T] = ...) -> _T: ...
def load_config(cfile_stem: str, use: Literal['local', 'global', 'system', 'default'] = 'local', default_path: Path | None = None, ctype: Any = None):

    cfile_name = cfile_stem + '.json'

    config_file = (
        found if (flg :=       (use == 'local'  )) and (found := (CPATH['local' ] / cfile_name)).exists() else
        found if (flg := flg | (use == 'global' )) and (found := (CPATH['global'] / cfile_name)).exists() else
        found if (flg := flg | (use == 'system' )) and (found := (CPATH['system'] / cfile_name)).exists() else
        found if default_path and (found := _LIBRARY_ROOT / default_path / cfile_name).exists() else
        # bellow code will delete at version 0.3
        # CPATH['default'] / cfile_name
        (found := _find(Path.exists, (
            _LIBRARY_ROOT / p.format(cfile_stem=cfile_stem) / cfile_name for p in DPATH
        ), None))
    )

    try:
        return json.load(open(config_file))
    except TypeError:
        raise FileNotFoundError(f'{config_file} is a non-existent item')
    except FileNotFoundError:
        raise FileNotFoundError(f'No such file or directory: {config_file}, at finding step \'{flg}\'')

def decompose_keys(obj_temp, keys: list[str]) -> tuple[dict, Any, int] | tuple[list, Any, str] | tuple[None, Any, None]:
    obj_prev = None
    k = None
    for i, k in enumerate(keys):
        if isinstance(obj_temp, list):
            try:
                obj_prev = obj_temp
                obj_temp = obj_temp[int(k)]
            except ValueError:
                raise KeyError(f'refered object is list but key is invalid literal for int() with base 10: \'{k}\'')
            except IndexError:
                raise KeyError(f'list index out of range: {int(k)}')
        elif isinstance(obj_temp, dict):
            try:
                obj_prev = obj_temp
                obj_temp = obj_temp[k]
            except KeyError:
                raise KeyError(f'key {k} of {keys} is not found')
        else:
            raise KeyError(f'refered object do not have any children: {obj_temp}')
    return obj_prev, obj_temp, k
