from pytower import tower
from pytower.suitebro import Suitebro, TowerObject
from pytower.tower import ToolParameterInfo
from pytower.util import xyz

TOOL_NAME = 'Translate'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/kluberge/PyTower/blob/main/tools/translate.py'
INFO = '''Translates selection a specified amount (in world coordinates)'''
PARAMETERS = {'offset': ToolParameterInfo(dtype=xyz, description='Translation offset')}


def main(suitebro: Suitebro, selection: list[TowerObject], params: dict):
    offset = params['offset']

    # Scale about the origin
    for obj in selection:
        obj.position += offset


if __name__ == '__main__':
    tower.main('CondoData', tooling_injection=main, args={'parameters': ['offset=50,50,50']})
