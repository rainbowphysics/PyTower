from pytower import tower
from pytower.suitebro import Suitebro
from pytower.tool_lib import ParameterDict

TOOL_NAME = 'Grouper'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/grouper.py'
INFO = '''Groups the selection'''


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    selection.group()
