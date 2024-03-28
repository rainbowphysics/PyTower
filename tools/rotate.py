from pytower import tower
from pytower.selection import Selection
from pytower.suitebro import Suitebro, TowerObject
from pytower.tower import ToolParameterInfo, ParameterDict
from pytower.util import xyz

import numpy as np
from scipy.spatial.transform import Rotation as R

TOOL_NAME = 'Rotate'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/kluberge/PyTower/blob/main/tools/rotate.py'
INFO = '''Rotates selection a specified amount (in world coordinates)'''
PARAMETERS = {'rotation': ToolParameterInfo(dtype=xyz, description='Rotation to perform (in Euler angles and degrees)'),
              'local': ToolParameterInfo(dtype=bool, description='Whether to only rotate locally', default=False)}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    rot = params.rotation
    r = R.from_euler('xyz', rot, degrees=True)
    centroid = sum([obj.position for obj in selection]) / len(selection)

    for obj in selection:
        # Since obj.rotation is quaternion, need to convert to/from
        q = R.from_quat(obj.rotation)
        p = r * q
        obj.rotation = p.as_quat()

        #TODO special treatment of groups--groups are still considered local

        if not params.local:
            # Rotate positions around centroid with help from scipy
            obj.position -= centroid
            obj.position = r.apply(obj.position)
            obj.position += centroid


if __name__ == '__main__':
    tower.run('CondoData', main, params=['rotation=0,0,45'])
