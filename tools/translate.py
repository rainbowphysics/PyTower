from pytower import tower
from pytower.selection import Selection
from pytower.suitebro import Suitebro, TowerObject
from pytower.tower import ToolParameterInfo, ParameterDict
from pytower.util import xyz

from scipy.spatial.transform import Rotation as R

TOOL_NAME = 'Translate'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/translate.py'
INFO = '''Translates selection a specified amount (in world coordinates)'''
PARAMETERS = {'offset': ToolParameterInfo(dtype=xyz, description='Translation offset'),
              'local': ToolParameterInfo(dtype=bool, description='Whether to translate in local coordinates',
                                         default=False)}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    offset = params.offset

    # Translate in world coordinates, easy
    if not params.local:
        for obj in selection:
            obj.position += offset
        return

    # Otherwise, we translate in local coordinates

    # Start by taking the standard basis in world coordinates
    xhat = xyz(1, 0, 0)
    yhat = xyz(0, 1, 0)
    zhat = xyz(0, 0, 1)
    std_basis = [xhat, yhat, zhat]

    for obj in selection:
        # Convert obj.rotation to a scipy rotation
        r = R.from_quat(obj.rotation)
        # Rotate each of the standard basis vectors by obj.rotation to get local coordinates
        xlocal, ylocal, zlocal = [r.apply(basis_vec) for basis_vec in std_basis]
        # Now use this to peform a local translation
        obj.position += offset[0] * xlocal + offset[1] * ylocal + offset[2] * zlocal


if __name__ == '__main__':
    tower.run('CondoData', main, params=['offset=50,50,50'])
