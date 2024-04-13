from pytower import tower
from pytower.copy import copy_selection
from pytower.selection import Selection
from pytower.suitebro import Suitebro
from pytower.tool_lib import ToolParameterInfo, ParameterDict
from pytower.tools import translate
from pytower.util import xyz

TOOL_NAME = 'Duplicate'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/duplicate.py'
INFO = '''Duplicates selection (with optional offset)'''
PARAMETERS = {'offset': ToolParameterInfo(dtype=xyz, description='Translation offset', default=xyz(0.0, 0.0, 0.0)),
              'local': ToolParameterInfo(dtype=bool, description='Whether to offset using local coordinates',
                                         default=False)}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    duplicated = copy_selection(selection)
    save.add_objects(duplicated)

    translate.main(save, duplicated, params)


if __name__ == '__main__':
    tower.run('CondoData', main, params=['offset=50,50,50'])
