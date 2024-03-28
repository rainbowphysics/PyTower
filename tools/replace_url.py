from pytower import tower
from pytower.selection import Selection
from pytower.suitebro import Suitebro, TowerObject
from pytower.tower import ToolParameterInfo, ParameterDict
from pytower.util import xyz, xyzint

import tools.set_url

TOOL_NAME = 'ReplaceURL'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/replace_url.py'
INFO = '''Replaces URL on canvas objects in the given selection.'''
PARAMETERS = {'url': ToolParameterInfo(dtype=str, description='URL to set'),
              'replace': ToolParameterInfo(dtype=str, description='URL to replace')}


def should_replace(obj: TowerObject, url: str) -> bool:
    if not obj.is_canvas():
        return False

    return obj.is_canvas() and obj.properties['properties']['URL']['StrProperty'] == url


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    selection = [obj for obj in selection if should_replace(obj, params.replace)]
    tools.set_url.main(save, selection, params)


if __name__ == '__main__':
    tower.run('CondoData', main, params=['url=https://i.imgur.com/V0pIX9G.png'])
