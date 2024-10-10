import math

from pytower.copy import copy_selection
from pytower.selection import Selection
from pytower.suitebro import Suitebro
from pytower.tools import rotate
from pytower.tool_lib import ToolParameterInfo, ParameterDict
from pytower.util import xyz

TOOL_NAME = 'Cylinder'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/cylinder.py'
INFO = '''Uses selection to form a cylinder centered at <center> of radius <radius> and height <height>'''
PARAMETERS = {'radius': ToolParameterInfo(dtype=float, description='radius of cylinder'),
              'height': ToolParameterInfo(dtype=float, description='height of cylinder'),
              'r_segments': ToolParameterInfo(dtype=int, description='number of radial segments', default=20),
              'h_segments': ToolParameterInfo(dtype=int, description='number of height segments', default=10),
              'rotation': ToolParameterInfo(dtype=xyz, description='x,y,z euler angle offset', default=xyz(0.0, 0.0, 0.0)),
              'local': ToolParameterInfo(dtype=bool, description='Whether to only rotate locally', default=False)}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    # Get tile/offset parameters, and handle edge-case for 0-entries
    r = params.radius
    for nt in range(params.r_segments):
        for nh in range(params.h_segments):
            theta = nt * 2 * math.pi / params.r_segments
            z_offset = nh * params.height / params.h_segments

            # Copy selection
            copies = copy_selection(selection)

            # Rotate then set position of copy
            deg = math.degrees(theta)
            params.rotation.z += deg
            rotate.main(save, copies, params)
            params.rotation.z -= deg

            offset = xyz(r * math.cos(theta), r * math.sin(theta), z_offset)
            for obj in copies:
                obj.position += offset

            # Add copies to save
            save.add_objects(copies)
