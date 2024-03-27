from pytower import tower
from pytower.selection import Selection
from pytower.suitebro import Suitebro, TowerObject
from pytower.tower import ToolParameterInfo, ParameterDict
from pytower.util import xyz, xyzint

TOOL_NAME = 'Set'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/kluberge/PyTower/blob/main/tools/set.py'
INFO = '''Sets materials on canvas objects in the given selection.'''
PARAMETERS = {'material': ToolParameterInfo(dtype=str, description='Material to apply')}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    mat = params.material
    for obj in selection:
        item_props = obj.item['properties']

        # Skip over non-canvas items
        if not obj.is_canvas():
            continue

        # Remove URL entry from object header if exists
        if 'URL' in item_props:
            del item_props['URL']

        # Set material
        item_props['SurfaceMaterial'] = {'ObjectProperty': mat}

        # Ensure other object properties agree
        obj.properties['properties']['SurfaceMaterial'] = {'ObjectProperty': mat}
        obj.properties['properties']['URL'] = {'StrProperty': ''}


if __name__ == '__main__':
    tower.run('CondoData', main,
              params=['material=/Game/Materials/Lobby/Arcade/Cabinets/ArcadeGlassNew.ArcadeGlassNew'])
