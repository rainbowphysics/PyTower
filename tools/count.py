from pytower.logging import *
from pytower.selection import Selection
from pytower.suitebro import Suitebro
from pytower.tool_lib import ParameterDict

TOOL_NAME = 'Count'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/count.py'
INFO = '''Counts the number of objects in a map'''
NO_WRITE = True


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    info('Item count:')
    for name, count in save.item_count().items():
        info(f'{count:>9,}x {name}')
