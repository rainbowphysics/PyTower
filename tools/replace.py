from pytower import tower
from pytower.selection import Selection
from pytower.suitebro import Suitebro, TowerObject
from pytower.tools import set
from pytower.tool_lib import ToolParameterInfo, ParameterDict

TOOL_NAME = 'Replace'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/replace.py'
INFO = '''Replace materials on canvas objects in the given selection.'''
PARAMETERS = {'replace': ToolParameterInfo(dtype=str, description='Material to replace'),
              'material': ToolParameterInfo(dtype=str, description='Replacement material to use instead')}


def should_replace(obj: TowerObject, material: str) -> bool:
    if not obj.is_canvas():
        return False

    return obj.is_canvas() and obj.properties['properties']['SurfaceMaterial']['Object']['value'] == material


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    selection = Selection({obj for obj in selection if should_replace(obj, params.replace)})
    set.main(save, selection, params)


if __name__ == '__main__':
    tower.run('CondoData', main,
              params=['material=/Game/Materials/Lobby/Arcade/Cabinets/ArcadeGlassNew.ArcadeGlassNew'])
