from pytower import tower
from pytower.suitebro import Suitebro, TowerObject
from pytower.tower import ToolParameterInfo
from pytower.util import xyz

TOOL_NAME = 'Scale'
VERSION = '1.0'
AUTHOR = 'Physics System'
URL = 'https://github.com/kluberge/PyTower/blob/main/pytower/tools/scale.py'
INFO = '''Scales selection up, either around the centroid (default) or world origin (origin=True)'''
PARAMETERS = {'scale': ToolParameterInfo(dtype=xyz, description='Scaling factor'),
              'origin': ToolParameterInfo(dtype=bool, description='Whether to scale around the origin', optional=True)}


def main(suitebro: Suitebro, selection: list[TowerObject], params: dict):
    scale = params['scale']

    # Optional parameter
    use_origin = 'origin' in params and params['origin']

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
    tower.main('CondoData', tooling_injection=main, args={'parameters': ['scale=2,2,2']})
