from pytower import tower
from pytower.selection import Selection
from pytower.suitebro import Suitebro
from pytower.tool_lib import ToolParameterInfo, ParameterDict

TOOL_NAME = 'SetURL'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/set_url.py'
INFO = '''Sets URL on canvas objects in the given selection.'''
PARAMETERS = {'url': ToolParameterInfo(dtype=str, description='URL to set')}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    url = params.url
    for obj in selection:
        if obj.item is None or obj.properties is None:
            continue

        item_props = obj.item['properties']

        # Skip over non-canvas items
        if not obj.is_canvas():
            continue

        # Remove SurfaceMaterial entry from object header if exists
        if 'SurfaceMaterial' in item_props:
            del item_props['SurfaceMaterial']

        # Set URL
        item_props['URL'] = {'Str': {'value': url}}

        # Ensure other object properties agree
        obj.properties['properties']['SurfaceMaterial'] = {'Object': {'value': ''}}
        obj.properties['properties']['URL'] = {'Str': {'value': url}}


if __name__ == '__main__':
    tower.run('CondoData', main, params=['url=https://i.imgur.com/V0pIX9G.png'])
