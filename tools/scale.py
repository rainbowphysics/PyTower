from pytower import tower
from pytower.selection import Selection
from pytower.suitebro import Suitebro
from pytower.tower import ToolParameterInfo, ParameterDict

TOOL_NAME = 'Scale'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/rainbowphysics/PyTower/blob/main/tools/scale.py'
INFO = '''Scales selection up, either around the centroid (default) or world origin (origin=True)'''
PARAMETERS = {'scale': ToolParameterInfo(dtype=float, description='Scaling factor'),
              'origin': ToolParameterInfo(dtype=bool, description='Whether to scale around the origin', default=False)}


def main(save: Suitebro, selection: Selection, params: ParameterDict):
    scale = params.scale

    # Optional parameter
    use_origin = 'origin' in params and params.origin

    centroid = sum([obj.position for obj in selection]) / len(selection)

    # When not using the origin to scale, we need to shift the coordinates so that the centroid *becomes* the origin
    if not use_origin:
        for obj in selection:
            obj.position -= centroid

    # Scale about the origin
    for obj in selection:
        obj.position *= scale
        obj.scale *= scale

    # Shift coordinates back to world coordinates
    if not use_origin:
        for obj in selection:
            obj.position += centroid


if __name__ == '__main__':
    tower.run('CondoData', main, params=['scale=10'])
