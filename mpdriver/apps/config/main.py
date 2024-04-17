import json

from ...core.config import CPATH, load_config
from ...core.main_base import Verbose
from .args import ConfigArgs

def app_main(ns: ConfigArgs):

    verbose = Verbose(ns.verbose)

    cfile_name, *keys = ckey = ns.key.split('.')
    cfile_name += '.json'

    config_file = (
        found if (usr :=        (ns.file_local  and 'local'  )) and (found := (CPATH['local' ] / cfile_name)).exists() else
        found if (usr := usr or (ns.file_global and 'global' )) and (found := (CPATH['global'] / cfile_name)).exists() else
        found if (usr := usr or (ns.file_system and 'system' )) and (found := (CPATH['system'] / cfile_name)).exists() else
        (usr := usr or 'default') and (found := CPATH['default'] / cfile_name)
    )

    if ns.value is None and usr != found.parent.name:
        verbose.message('warning', f'use \'{usr}\' given, but don\'t found it, so use \'{found.parent.name}\'.')

    verbose.message('info', f'load {config_file}')
    config = json.load(open(config_file))

    obj_prev = None
    obj_temp = config
    for i, k in enumerate(keys):
        if isinstance(obj_temp, list):
            obj_prev = obj_temp
            obj_temp = obj_temp[int(k)]
        elif isinstance(obj_temp, dict):
            obj_prev = obj_temp
            obj_temp = obj_temp[k]
        else:
            verbose.message('error', f'key \'{"".join(ckey[:i+2])}\' is not found')
            return

    if ns.value is None: # GET
        verbose.message('info', f'get from \'{ns.key}\'')
        print(json.dumps(obj_temp, indent=4))
        return

    # else SET
    verbose.message('info', f'set \'{ns.value}\' to \'{ns.key}\' ')
    obj_prev[k] = json.loads(ns.value)

    if usr == 'default':
        verbose.message('warning', 'can\'t set to default. nothing to do.')
        return 

    json.dump(config, open(CPATH[usr] / cfile_name, 'w'), indent=4)
    
    verbose.message('info', 'bye.')