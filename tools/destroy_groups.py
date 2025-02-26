from pytower.selection import Selection
from pytower.suitebro import Suitebro
from pytower.tool_lib import ParameterDict

TOOL_NAME = 'DestroyGroups'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/destroy_groups.py'
INFO = '''Destroys all groups in selection (useful for when large groups cause lag)'''


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    selection.destroy_groups()
