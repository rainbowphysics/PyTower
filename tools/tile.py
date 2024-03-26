from pytower import tower
from pytower.suitebro import Suitebro, TowerObject
from pytower.tower import ToolParameterInfo
from pytower.util import xyz, xyzint

TOOL_NAME = 'Tile'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/kluberge/PyTower/blob/main/pytower/tools/tile.py'
INFO = '''Tiles selection <tile> times in each dimension at offsets <offset>.'''
PARAMETERS = {'tile': ToolParameterInfo(dtype=xyzint, description='x,y,z tiling in each dimension'),
              'offset': ToolParameterInfo(dtype=xyz, description='x,y,z offsets')}


def main(suitebro: Suitebro, selection: list[TowerObject], params):
    nx, ny, nz = params['tile']
    dx, dy, dz = params['offset']
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                # Skip tiling origin
                if x == 0 and y == 0 and z == 0:
                    continue

                # Copy selection
                copies = TowerObject.copy_group(selection)

                # Set position of copy
                offset = xyz(x * dx, y * dy, z * dz)
                for obj in copies:
                    obj.position += offset

                # Add copies to save
                suitebro.add_objects(copies)


if __name__ == '__main__':
    tower.main('CondoData', main, args={'parameters': ['tile=5,5,5', 'offset=70,70,70']})
