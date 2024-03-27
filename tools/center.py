from pytower import tower
from pytower.suitebro import Suitebro, TowerObject
from pytower.tower import ToolParameterInfo, ParameterDict
from pytower.util import xyz

TOOL_NAME = 'Center'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/kluberge/PyTower/blob/main/tools/center.py'
INFO = '''Centers selection at the world origin'''
PARAMETERS = {'offset': ToolParameterInfo(dtype=xyz, description='Optional offset', default=xyz(0, 0, 0))}


def main(save: Suitebro, selection: list[TowerObject], params: ParameterDict):
    offset = params.offset
    centroid = sum([obj.position for obj in selection]) / len(selection)

    for obj in selection:
        # Move so that the centroid becomes the origin
        obj.position -= centroid

        # Add optional offset
        obj.position += offset


if __name__ == '__main__':
    tower.run('CondoData', main, params=['offset=0,0,300'])
