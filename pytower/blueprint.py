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
from .util import xyz, XYZ, XYZW

BLUEPRINT_DIR = os.path.join(root_directory, 'blueprints')

MARKER_SELECTOR = CustomNameSelector('PyMarker')


def make_blueprint(name: str, selection: Selection, anchor_mode: str = 'centroid') -> bool:
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

    anchor_mode = anchor_mode.strip().casefold()
    if anchor_mode not in ['centroid', 'lowest', 'none']:
        error(f'{anchor_mode} is not a valid anchor mode! Must be: centroid, lowest, or none')
        return False

    match anchor_mode:
        case 'centroid':
            centroid = selection.centroid
            min_z = float('inf')
            for obj in selection:
                min_z = min(obj.position.z, min_z)

            blueprint_origin = xyz(centroid.x, centroid.y, min_z)
        case 'lowest':
            min_z = float('inf')
            lowest_obj = None
            for obj in selection:
                if obj.position.z < min_z:
                    min_z = obj.position.z
                    lowest_obj = obj

            blueprint_origin = lowest_obj.position
        case _:
            blueprint_origin = xyz(0.0, 0.0, 0.0)


    for obj in selection:
        obj.position -= blueprint_origin

    with open(blueprint_path, 'w') as fd:
        json.dump(selection.to_dict(), fd, indent=2)

    return True

def _copy_blueprint(save: Suitebro, blueprint: Selection, marker_position: XYZ, marker_rotation: XYZW,
                    marker_scale: XYZ, group: bool = False, marker: TowerObject | None = None):
    bp_copy = copy_selection(blueprint)
    if group:
        bp_copy.group()
    save.add_objects(list(bp_copy))

    # Apply marker scale
    scale.main(save, bp_copy, ParameterDict({'scale': max(marker_scale), 'origin': True}))
    # Apply marker's rotation
    r = R.from_quat(marker_rotation)
    rotate.main(save, bp_copy, ParameterDict({'rotation': r.as_euler('xyz', degrees=True), 'local': False}))
    # Finally apply marker translation
    translate.main(save, bp_copy, ParameterDict({'offset': marker_position, 'local': False}))

    # Delete marker
    if marker is not None:
        save.remove_object(marker)

def place_blueprint(name: str, save: Suitebro, force: bool = False, group: bool = False) -> bool:
    blueprint_path = Path(BLUEPRINT_DIR) / Path(f'{name}.json')

    if not blueprint_path.exists() or not blueprint_path.is_file():
        error(f'Could not find blueprint {name}!')
        return False

    with open(blueprint_path, 'r', encoding='utf-8') as fd:
        data = json.load(fd)

    blueprint = Selection(TowerObject.deserialize_objects(data))
    markers = MARKER_SELECTOR.select(Selection(save.objects))

    if len(markers) == 0:
        if not force:
            return False

        _copy_blueprint(save, blueprint, xyz(0, 0, 0), XYZW(0, 0, 0, 1), xyz(1, 1, 1), group=group, marker=None)
        return True

    for marker in markers:
        _copy_blueprint(save, blueprint, marker.position, marker.rotation, marker.scale, group=group, marker=marker)

    return True

