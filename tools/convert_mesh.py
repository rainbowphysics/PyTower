from scipy.spatial.transform import Rotation as R

from pytower import tower
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
PARAMETERS = {'filename': ToolParameterInfo(dtype=str, description='Filename of 3D model')}

def main(save: Suitebro, selection: Selection, params: ParameterDict):
    mesh = load_mesh(params.filename)
    convert_mesh(save, mesh)


if __name__ == '__main__':
    tower.run('../saves/blank', main, params=['filename=../cube.obj'])
