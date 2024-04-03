from pytower import tower
from pytower.selection import Selection, ObjectNameSelector
from pytower.suitebro import Suitebro
from pytower.tower import ParameterDict

TOOL_NAME = 'Filter'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/filter.py'
INFO = '''Filters the save so that only the items in selection remain'''


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    # Filter out everything except for metadata objects
    save.objects = [obj for obj in save.objects if obj.item is None or obj in selection]

    # Update group metadata
    save.update_groups_meta()


if __name__ == '__main__':
    tower.run('popcorn', main, selector=ObjectNameSelector('CanvasCube'))
