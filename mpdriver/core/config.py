from typing import Literal
from pathlib import Path
import json

CPATH: dict[Literal['local', 'global', 'system', 'default'], Path] = { # ORDERD
    'local': Path().resolve() / '.mpdriver',
    'global': Path('~').resolve() / '.mpdriver',
    'system': Path(__file__).resolve().parents[1] / 'config/system',
    'default': Path(__file__).resolve().parents[1] / 'config/default'
}

def load_config(cfile_stem: str, use: Literal['local', 'global', 'system', 'default'] = 'local'):

    cfile_name = cfile_stem + '.json'

    config_file = (
        found if (flg :=       (use == 'local'  )) and (found := (CPATH['local' ] / cfile_name)).exists() else
        found if (flg := flg | (use == 'global' )) and (found := (CPATH['global'] / cfile_name)).exists() else
        found if (flg := flg | (use == 'system' )) and (found := (CPATH['system'] / cfile_name)).exists() else
        (found := CPATH['default'] / cfile_name)
    )

    return json.load(open(config_file))
