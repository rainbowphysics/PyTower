import json
import logging
import os
from subprocess import Popen, PIPE

from . import root_directory
from .selection import Selection
from .object import TowerObject

ITEM_ONLY_OBJECTS = ['SDNL_ArmorPickup', 'AmmoPickup', 'HealthPickup', 'GW_SDNLFlag', 'GW_SDNLOddball',
                     'WeaponPickupIO']

IO_GW_ITEMS = ['AmmoPickup', 'CustomSpawnPoint', 'HealthPickup', 'SDNL_ArmorPickup', 'GW_SDNLOddball', 'GW_SDNLFlag',
               'GW_BallRaceFinish', 'GW_BallRaceSpawn', 'LaserBeam', 'LeverBasic', 'ButtonShapes', 'PhysicsSlot',
               'WeaponPickupIO', 'ButtonCanvas', 'LocationVolumeIO', 'DamageHealVolume', 'BlockingVolume',
               'WaterVolume', 'CommentVolume', 'DialogueVolume', 'GravityVolume', 'ButtonVolume', 'HitTargetVolume',
               'LadderVolume', 'PlayerMovementVolume', 'PostProcessVolume', 'PushVolume', 'SizeVolume',
               'SkyProcessVolume', 'SpawnPointTagVolume', 'TriggerVolume', 'WeaponStripVolume', 'TeleportVolume',
               'GameWorldEvents', 'LaserBeamReciever', 'Mover', 'Counter', 'LogicGateAnd', 'SwitchBoolean',
               'LogicGateNot', 'LogicGateOr', 'LogicGateXor', 'Random', 'Relay', 'Timer', 'Toggle', 'WorldControl',
               'LeverLightSwitch', 'MoverAdvanced', 'MoverPlayerSlide', 'MoverTrain']


class Suitebro:
    def __init__(self, filename: str, directory: str, data: dict):
        self.filename = filename
        self.directory = directory
        self.data: dict = data

        # Parse objects
        prop_section = self.data['properties']
        item_section = self.data['items']
        num_props = len(prop_section)
        num_items = len(item_section)
        self.objects: list[TowerObject | None] = [None] * (num_items + num_props)

        # This algorithm handles inserting TowerObjects from the (indexed) json by handling three cases:
        #  Case 1: There is an item but no corresponding property
        #  Case 2 (Most likely): There is an item and a corresponding property
        #  Case 3: There is no item and just a property
        item_idx = 0
        prop_idx = 0
        x = 0
        while item_idx < num_items or prop_idx < num_props:
            p = prop_section[prop_idx] if prop_idx < num_props else None
            i = item_section[item_idx] if item_idx < num_items else None
            # print(p['name'] if p is not None else None)
            # print(i['name'] if i is not None else None)
            if i is not None and i['name'] in ITEM_ONLY_OBJECTS:
                self.objects[x] = TowerObject(item=i, properties=None)
                item_idx += 1
            elif i is not None and p is not None and p['name'].startswith(i['name']):
                self.objects[x] = TowerObject(item=i, properties=p)
                item_idx += 1
                prop_idx += 1
            elif p is not None:
                self.objects[x] = TowerObject(item=None, properties=p)
                prop_idx += 1
            x += 1

        # Now cull Nones at the end of array
        size = self.objects.index(None)
        self.objects = self.objects[:size]

    def add_object(self, obj):
        self.objects += [obj]

    def add_objects(self, objs):
        self.objects += objs

    def find_item(self, name: str) -> TowerObject | None:
        for obj in self.objects:
            if obj.matches_name(name):
                return obj
        return None

    def get_groups_meta(self):
        return self.data['groups']

    # TODO Definitely a better way to do this
    def get_max_groupid(self):
        sel = Selection(self.objects)
        # Get the max group_id tuple in group and get its id (first slot of tuple)
        return max(sel.groups(), key=lambda group_data: group_data[0])[0]

    def update_groups_meta(self):
        sel = Selection(self.objects)
        group_data = []
        for group_id, group in sel.groups():
            group_data.append({'group_id': group_id, 'item_count': len(group)})
        self.data['groups'] = group_data

    # Returns all non-property TowerObjects
    def items(self) -> list[TowerObject]:
        return [obj for obj in self.objects if obj.item is not None]

    def inventory_items(self) -> list[TowerObject]:
        return [obj for obj in self.objects if obj.item is not None and obj.properties is not None
                and obj.get_name() not in IO_GW_ITEMS]

    # Convert item list back into a dict
    def to_dict(self):
        new_dict = {}

        # Update groups based on group ids and info
        self.update_groups_meta()

        for k, v in self.data.items():
            if k != 'items' and k != 'properties':
                new_dict[k] = v

        self.objects.sort()

        num_obj = len(self.objects)
        item_arr = [None] * num_obj
        prop_arr = [None] * num_obj

        item_idx = 0
        prop_idx = 0

        last_name = None
        last_num = 0
        for obj in self.objects:
            if obj.item is not None:
                item_arr[item_idx] = obj.item
                item_idx += 1
            if obj.properties is not None:
                # Name fuckery TODO determine if the naming even matters
                if obj.item is not None:
                    name_split = obj.properties['name'].split('_')
                    root_name = '_'.join(name_split[:-1])

                    if last_name == root_name:
                        last_num += 1
                    else:
                        last_num = 0

                    obj.properties['name'] = root_name + '_' + str(last_num)

                    last_name = root_name

                # Now actually add to prop_arr
                prop_arr[prop_idx] = obj.properties
                prop_idx += 1

        item_arr = item_arr[:item_idx]
        prop_arr = prop_arr[:prop_idx]

        # Finally set new dictionary and return
        new_dict['items'] = item_arr
        new_dict['properties'] = prop_arr
        return new_dict

    def __repl__(self):
        return f'Suitebro({self.data}, {self.objects})'

    def __iter__(self):
        for obj in self.objects:
            yield obj


# _active_saves is a stack
_active_save: Suitebro | None = None


def get_active_save() -> Suitebro | None:
    return _active_save


def run_suitebro_parser(input_path: str, to_save: bool, output_path: str | None = None,
                        overwrite: bool = False) -> bool:
    curr_cwd = os.getcwd()
    suitebro_path = os.path.join(root_directory, 'tower-unite-suitebro')
    os.chdir(suitebro_path)

    process = Popen(f'cargo run --release {"to-save" if to_save else "to-json"} {"-!" if overwrite else ""}'
                    f' -i \"{input_path}\" -o \"{output_path}\"', stdout=PIPE, shell=True)
    (output, err) = process.communicate()
    # print(output, file=sys.stderr)
    for line in output.splitlines(False):
        print(line.decode('ascii'))

    exit_code = process.wait()

    if exit_code != 0:
        logging.error('Suitebro parser did not complete successfully!')
        return False

    os.chdir(curr_cwd)


def load_suitebro(filename: str, only_json=False) -> Suitebro:
    abs_filepath = os.path.realpath(filename)
    in_dir = os.path.dirname(abs_filepath)
    json_output_path = os.path.join(in_dir, os.path.basename(abs_filepath) + ".json")

    if not only_json:
        run_suitebro_parser(abs_filepath, False, json_output_path, overwrite=True)

    logging.info('Loading JSON file...')
    with open(json_output_path, 'r') as fd:
        save_json = json.load(fd)

    save = Suitebro(os.path.basename(abs_filepath), in_dir, save_json)

    global _active_save
    _active_save = save

    return save


def save_suitebro(save: Suitebro, filename: str, only_json=False):
    abs_filepath = os.path.realpath(filename)
    out_dir = os.path.dirname(abs_filepath)
    json_final_path = os.path.join(save.directory, f'{save.filename}.json')
    final_output_path = os.path.join(out_dir, f'{filename}')

    with open(json_final_path, 'w') as fd:
        json.dump(save.to_dict(), fd, indent=2)

    # Finally run!
    if not only_json:
        run_suitebro_parser(json_final_path, True, final_output_path, overwrite=True)
