from pytower import tower
from pytower.copy import copy_selection
from pytower.selection import Selection
from pytower.suitebro import Suitebro
from pytower.tool_lib import ToolParameterInfo, ParameterDict
from pytower.util import xyz, xyzint, xyz_max

TOOL_NAME = 'Tile'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/tile.py'
INFO = '''Tiles selection <tile> times in each dimension at offsets <offset>.'''
PARAMETERS = {'tile': ToolParameterInfo(dtype=xyzint, description='x,y,z tiling in each dimension'),
              'offset': ToolParameterInfo(dtype=xyz, description='x,y,z offsets')}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    # Get tile/offset parameters, and handle edge-case for 0-entries
    nx, ny, nz = xyz_max(params.tile, xyzint(1, 1, 1))
    dx, dy, dz = params.offset
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                # Skip tiling origin
                if x == 0 and y == 0 and z == 0:
                    continue

                # Copy selection
                copies = copy_selection(selection)

                # Set position of copy
                offset = xyz(x * dx, y * dy, z * dz)
                for obj in copies:
                    obj.position += offset

                # Add copies to save
                save.add_objects(copies)


if __name__ == '__main__':
    tower.run('CondoData', main, params=['tile=5,5,5', 'offset=70,70,70'])
