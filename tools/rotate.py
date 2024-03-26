from pytower import tower
from pytower.suitebro import Suitebro, TowerObject
from pytower.tower import ToolParameterInfo
from pytower.util import xyz

import numpy as np
from scipy.spatial.transform import Rotation as R

TOOL_NAME = 'Rotate'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/kluberge/PyTower/blob/main/tools/rotate.py'
INFO = '''Rotates selection a specified amount (in world coordinates)'''
PARAMETERS = {'rotation': ToolParameterInfo(dtype=xyz, description='Rotation to perform (in Euler angles and degrees)')}


def main(suitebro: Suitebro, selection: list[TowerObject], params: dict):
    rot = params['rotation']
    r = R.from_euler('xyz', rot, degrees=True)
    centroid = sum([obj.position for obj in selection]) / len(selection)

    for obj in selection:
        obj.rotation += rot

        # Rotate positions around centroid with help from scipy
        obj.position -= centroid
        obj.position = r.apply(obj.position)
        obj.position += centroid


if __name__ == '__main__':
    tower.main('CondoData', tooling_injection=main, args={'parameters': ['rotation=0,0,45']})
