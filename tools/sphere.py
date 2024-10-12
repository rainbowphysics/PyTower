import math
from scipy.spatial.transform import Rotation as R

from pytower import tower
from pytower.copy import copy_selection
from pytower.selection import Selection
from pytower.suitebro import Suitebro
from pytower.tools import rotate
from pytower.tool_lib import ToolParameterInfo, ParameterDict
from pytower.util import xyz, xyzint, XYZInt

TOOL_NAME = 'Sphere'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/sphere.py'
INFO = '''(WIP) Uses selection to form a sphere of radius <radius>'''
PARAMETERS = {'radius': ToolParameterInfo(dtype=float, description='radius of cylinder'),
              'n_points': ToolParameterInfo(dtype=int, description='number of radial segments', default=200),
              'rotation': ToolParameterInfo(dtype=xyz, description='x,y,z euler angle offset', default=xyz(0.0, 0.0, 0.0)),
              'local': ToolParameterInfo(dtype=bool, description='Whether to only rotate locally', default=False)}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    # Get tile/offset parameters, and handle edge-case for 0-entries
    r = params.radius
    varphi = math.pi * (3 - math.sqrt(5))
    N = params.n_points
    for i in range(N):
        z = 1 - (2 * i) / float(N - 1)  # z goes from 1 to -1
        radius = math.sqrt(1 - z * z)  # Radius at z

        theta = varphi * i  # Golden angle increment
        phi = math.acos(z)
        offset = xyz(radius * math.cos(theta), radius * math.sin(theta), z) * r

        # Copy selection
        copies = copy_selection(selection)

        # Rotate then set position of copy
        deg_theta = math.degrees(theta)
        deg_phi = math.degrees(phi) - 90

        params.rotation.z += deg_theta
        params.rotation.y += deg_phi
        params.rotation.x += deg_theta
        rotate.main(save, copies, params)
        params.rotation.x -= deg_theta
        params.rotation.y -= deg_phi
        params.rotation.z -= deg_theta

        for obj in copies:
            obj.position += offset

        # Add copies to save
        save.add_objects(copies)
