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

from typing import Literal
from pathlib import Path
import json

_LIBRARY_ROOT = Path(__file__).resolve().parents[1]
CPATH: dict[Literal['local', 'global', 'system', 'default'], Path] = { # ORDERD
    'local': Path().resolve() / '.mpdriver',
    'global': Path('~').resolve() / '.mpdriver',
    'system': _LIBRARY_ROOT / 'config/system'
}

def load_config(cfile_stem: str, use: Literal['local', 'global', 'system', 'default'] = 'local', default_path: Path | None = None):

    cfile_name = cfile_stem + '.json'

    config_file = (
        found if (flg :=       (use == 'local'  )) and (found := (CPATH['local' ] / cfile_name)).exists() else
        found if (flg := flg | (use == 'global' )) and (found := (CPATH['global'] / cfile_name)).exists() else
        found if (flg := flg | (use == 'system' )) and (found := (CPATH['system'] / cfile_name)).exists() else
        found if default_path and (found := _LIBRARY_ROOT / default_path / cfile_name).exists() else
        # bellow code will delete at version 0.3
        CPATH['default'] / cfile_name
    )

    return json.load(open(config_file))
