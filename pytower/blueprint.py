import json
from pathlib import Path

from scipy.spatial.transform import Rotation as R

from .copy import copy_selection
from .logging import *
from .object import TowerObject
from .selection import Selection, CustomNameSelector
from .suitebro import Suitebro
from .tool_lib import ParameterDict
from .tools import rotate, scale, translate
from .util import xyz

BLUEPRINT_DIR = os.path.join(root_directory, 'blueprints')

MARKER_SELECTOR = CustomNameSelector('PyMarker')


def make_blueprint(name: str, selection: Selection) -> bool:
    if '..' in name:
        error('Using .. in blueprint path not supported')
        return False

    blueprint_path = Path(BLUEPRINT_DIR) / Path(f'{name}.json')

    if blueprint_path.exists() and not blueprint_path.is_file():
        error(f'{blueprint_path} already exists as a non-file object!')
        return False

    if blueprint_path.exists():
        warning(f'Blueprint {name} already exists.')
        response = input('Do you want to overwrite it? (Y/n): ')
        response = response.strip().casefold()
        if response != 'y' and response != 'ye' and response != 'yes':
            return False

    blueprint_path.parent.mkdir(parents=True, exist_ok=True)

    centroid = selection.centroid
    min_z = float('inf')
    for obj in selection:
        min_z = min(obj.position.z, min_z)

    blueprint_origin = xyz(centroid.x, centroid.y, min_z)
    for obj in selection:
        obj.position -= blueprint_origin

    with open(blueprint_path, 'w') as fd:
        json.dump(selection.to_dict(), fd, indent=2)

    return True

def place_blueprint(name: str, save: Suitebro) -> bool:
    blueprint_path = Path(BLUEPRINT_DIR) / Path(f'{name}.json')

    if not blueprint_path.exists() or not blueprint_path.is_file():
        error(f'Could not find blueprint {name}!')

    with open(blueprint_path, 'r', encoding='utf-8') as fd:
        data = json.load(fd)

    blueprint = Selection(TowerObject.deserialize_objects(data))
    markers = MARKER_SELECTOR.select(Selection(save.objects))
    placed = False
    for marker in markers:
        bp_copy = copy_selection(blueprint)
        save.add_objects(list(bp_copy))

        # Apply marker scale
        scale.main(save, bp_copy, ParameterDict({'scale': max(marker.scale), 'origin': True}))
        # Apply marker's rotation
        r = R.from_quat(marker.rotation)
        rotate.main(save, bp_copy, ParameterDict({'rotation': r.as_euler('xyz', degrees=True), 'local': False}))
        # Finally apply marker translation
        translate.main(save, bp_copy, ParameterDict({'offset': marker.position, 'local': False}))

        # Delete marker
        save.remove_object(marker)

        placed = True

    return placed

