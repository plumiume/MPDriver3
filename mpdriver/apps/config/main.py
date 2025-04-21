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
# limitations under the License.import json

import os
import json

from ...core.config import CPATH, load_config, decompose_keys
from ...core.main_base import Verbose
from .args import ConfigArgs

def app_main(ns: ConfigArgs):

    verbose = Verbose(ns.verbose)

    cfile_stem, *keys = ckey = ns.key.split('.')
    cfile_name = cfile_stem + '.json'

    if ns.file_local:
        use = 'local'
    elif ns.file_global:
        use = 'global'
    elif ns.file_system:
        use = 'system'
    else:
        use = 'default'

    if ns.from_template is not None:
        verbose.message('info', f'copy from \'{ns.from_template}\'')
        config = json.load(open(ns.from_template, 'r'))
    else:
        config = load_config(cfile_stem, use)

    try:
        obj_prev, obj_temp, k = decompose_keys(config, keys)
    except KeyError as e:
        verbose.message('error', *e.args)
        return

    if ns.value is None: # GET
        verbose.message('info', f'get from \'{ns.key}\'')
        print(json.dumps(obj_temp, indent=4))
        return

    # else SET
    verbose.message('info', f'set \'{ns.value}\' to \'{ns.key}\' ')
    if isinstance(obj_prev, list):
        obj_prev[int(k)] = json.loads(ns.value)
    elif isinstance(obj_prev, dict):
        obj_prev[k] = json.loads(ns.value)
    else:
        verbose.message('warning', 'can\'t set to non container object. nothing to do')

    if use == 'default':
        verbose.message('warning', 'can\'t set to default. nothing to do.')
        return 

    if not CPATH[use].exists():
        os.makedirs(CPATH[use])
    json.dump(config, open(CPATH[use] / cfile_name, 'w'), indent=4)

    verbose.message('info', 'bye.')