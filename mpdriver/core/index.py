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

from typing import Sequence, overload
from itertools import chain
from enum import IntEnum

def get_header(
    enum: type[IntEnum] | Sequence,
    indices: list[int | IntEnum],
    name_prefix: str = '',
    dim_names: Sequence[str] = ['X', 'Y', 'Z']
    ):

    if isinstance(enum, Sequence):
        def getter(idx: int):
            return enum[idx]
    elif issubclass(enum, IntEnum):
        def getter(idx: IntEnum):
            return enum(idx).name
    else:
        raise TypeError

    return list(chain.from_iterable(
        (f'{name_prefix}_{getter(idx)}_{dn}' for dn in dim_names)
        for idx in indices
    ))

@overload
def to_landmark_indices(enum: type[IntEnum], list_str: list[str] | None) -> list[IntEnum]: ...
@overload
def to_landmark_indices(seq_int: Sequence[int], list_int: list[int] | None) -> list[int]: ...
@overload
def to_landmark_indices(_enum: type[IntEnum] | Sequence[int] | None, _list: list[str | int] | None) -> list[IntEnum | int]: ...
def to_landmark_indices(_enum: type[IntEnum] | Sequence[int] | None, _list: list[str | int] | None) -> list[IntEnum | int]:

    if _enum is None:
        return slice(None)

    if _list is None:
        _list = _enum

    if isinstance(_enum, Sequence):
        return [_enum[i] for i in _list]

    elif issubclass(_enum, IntEnum):
        return [
            _enum[i] if isinstance(i, str) else _enum(i)
            for i in _list
        ]

    raise TypeError
