from scipy.spatial.transform import Rotation as R

from pytower import tower
from pytower.logging import *
from pytower.selection import Selection
from pytower.suitebro import Suitebro
from pytower.tool_lib import ToolParameterInfo, ParameterDict
from pytower.util import xyz
from pytower.mesh import convert_mesh, load_mesh

TOOL_NAME = 'ConvertMesh'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/convert_mesh.py'
INFO = '''Converts given mesh into wedges'''
PARAMETERS = {'filename': ToolParameterInfo(dtype=str, description='Filename of 3D model'),
              'offset': ToolParameterInfo(dtype=xyz, description='Translation offset', default=xyz(0.0, 0.0, 0.0)),
              'scale': ToolParameterInfo(dtype=float, description='Model scale', default=1.0)}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    # Load mesh
    mesh = load_mesh(params.filename)

    # Scale mesh BEFORE converting to canvas wedges
    mesh.triangles *= params.scale

    # Convert mesh and group together
    mesh_group_id = convert_mesh(save, mesh, offset=params.offset).group()
    success(f'Imported mesh {params.filename} with group:{mesh_group_id}')


if __name__ == '__main__':
    tower.run('../saves/blank', main, params=['filename=../bunny.obj', 'offset=0,0,300', 'scale=20'])
