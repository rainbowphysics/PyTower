import itertools
import json
import platform
import sys
from subprocess import Popen, PIPE
from typing import Any, Sequence, TypedDict

from .logging import *
from .object import TowerObject
from .selection import Selection


class Suitebro:
    """
    Suitebro file

    Abstraction over the input CondoData/.map file, representing parsed tower-unite-suitebro data

    Attributes:
        objects: The list of TowerObject instances contained in the Suitebro file
    """

    def __init__(self, filename: str, directory: str, data: dict[str, Any]):
        """
        Instantiates a new Suitebro instance based on the input filename and directory

        Args:
            filename: Name of file
            directory: Path to directory (can be relative or absolute)
            data: The raw json data from tower-unite-suitebro
        """
        self.filename = filename
        self.directory = directory
        self.data: dict[str, Any] = data

        self.objects = TowerObject.deserialize_objects(data)

    def add_object(self, obj: TowerObject):
        """
        Adds a new object to the Suitebro file

        Args:
            obj: The object to add
        """
        self.objects += [obj]

    def add_objects(self, objs: Sequence[TowerObject]):
        """
        Adds a list of objects to the Suitebro file

        Args:
            objs: The list of objects to add
        """
        self.objects += objs

    def remove_object(self, obj: TowerObject):
        """
        Removes object from the Suitebro file

        Args:
            obj: The object to remove
        """
        self.objects.remove(obj)

    def find_item(self, name: str) -> TowerObject | None:
        """
        Find a TowerObject by its name

        Args:
            name: The proper name or the nickname of the TowerObject

        Returns:
            The first TowerObject matching the name, if found, or else None
        """
        for obj in self.objects:
            if obj.matches_name(name):
                return obj
        return None

    def _get_groups_meta(self):
        return self.data['groups']

    def _update_groups_meta(self):
        class GroupData(TypedDict):
            group_id: int
            item_count: int

        sel = Selection(self.objects)
        group_data: list[GroupData] = []
        for group_id, group in sel.groups():
            group_data.append({'group_id': group_id, 'item_count': len(group)})
        self.data['groups'] = group_data

    def groups(self) -> set[tuple[int, Selection]]:
        """
        Calculates the groups present in the save

        Returns:
            The set of groups, as a set of tuples where the first slot is the group ID and the second slot is the
            corresponding Selection
        """
        sel = Selection(self.objects)
        return sel.groups()

    def get_max_groupid(self) -> int:
        """
        Returns:
            Maximum group ID present in the save
        """
        max_id = -1
        for obj in self.objects:
            max_id = max(obj.group_id, max_id)
        return max_id

    def group(self, objs: Selection, group_id: None | int = None) -> int:
        """
        Groups a selection of objects together

        Args:
            objs: Selection of objects to group
            group_id: (Optional) The group ID to use
        """
        new_group_id = self.get_max_groupid() + 1 if group_id is None else group_id
        for obj in objs:
            obj.group_id = new_group_id

        return new_group_id

    def items(self) -> list[TowerObject]:
        """
        Lists all non-property TowerObjects

        Returns:
            List containing all of the non-property TowerObject instances in this Suitebro
        """
        return [obj for obj in self.objects if obj.item is not None]

    def inventory_items(self) -> list[TowerObject]:
        """
        Lists all TowerObject instances that are non-property and are not I/O nor Game-World.

        This is equivalent to getting all items that exist in a player's inventory

        Returns:
            List of TowerObject instances in the Suitebro that exist in a player's Steam inventory
        """
        return [obj for obj in self.objects if obj.item is not None and obj.item['steam_item_id'] != 0]

    def _item_count(self, objs: Sequence[TowerObject]) -> dict[str, int]:
        ordered = sorted(objs, key=TowerObject.get_name)
        return {name: len(list(objs)) for name, objs in itertools.groupby(ordered, TowerObject.get_name)}

    def item_count(self) -> dict[str, int]:
        """
        Counts the number of items in the Suitebro file

        Returns:
            Dictionary where each key is the proper name of the object and the value is the number of instances
        """
        return self._item_count(self.items())

    def inventory_count(self) -> dict[str, int]:
        """
        Counts the number of inventory items in the Suitebro file

        Returns:
            Dictionary where each key is the proper name of the object and the value is the number of instances
        """
        objs = self.inventory_items()
        return self._item_count(objs)

    # Convert item list back into a dict
    def to_dict(self):
        """
        Converts the Suitebro object back into a dictionary, formatted in the tower-unite-suitebro style

        Returns:
            Serialized Suitebro representation that can be written to a file using json.dump
        """
        new_dict: dict[str, Any] = {}

        # Update groups based on group ids and info
        self._update_groups_meta()

        for k, v in self.data.items():
            if k != 'items' and k != 'properties':
                new_dict[k] = v

        serial_objs = Selection(self.objects).to_dict()
        new_dict['items'] = serial_objs['items']
        new_dict['properties'] = serial_objs['properties']

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


def get_suitebro_path():
    # For cases when want to build suitebro parser from source, for whatever reason
    from .config import CONFIG, KEY_FROM_SOURCE
    if CONFIG and CONFIG.get(KEY_FROM_SOURCE):
        source_dir = os.path.join(root_directory, 'tower-unite-suitebro')
        if os.path.isdir(source_dir):
            return source_dir
        else:
            critical('Could not find tower-unite-suitebro. Is suitebro installed in a folder named tower-unite-suitebro?')
            sys.exit(1)

    if sys.platform == 'win32':
        subdir = os.path.join(os.path.join('lib', 'win64'), 'tower-unite-save-x86_64-pc-windows-msvc.exe')
    elif sys.platform == 'darwin':
        machine = platform.machine().lower()
        is_arm = machine.startswith('arm') or machine.startswith('aarch') or platform.processor().lower() == 'apple arm'
        if is_arm:
            subdir = os.path.join(os.path.join('lib', 'apple-aarch64'), 'tower-unite-save-aarch64-apple-darwin')
        else:
            subdir = os.path.join(os.path.join('lib', 'apple-x86'), 'tower-unite-save-x86_64-apple-darwin')
    elif sys.platform == 'linux':
        is_docker = False
        with open('/proc/1/cgroup', 'rt') as f:
            for line in f:
                if 'docker' in line:
                    is_docker = True

        if is_docker:
            subdir = os.path.join(os.path.join('lib', 'linux-container'), 'tower-unite-save-x86_64-unknown-linux-musl')
        else:
            subdir = os.path.join(os.path.join('lib', 'linux'), 'tower-unite-save-x86_64-unknown-linux-gnu')
    else:
        critical(f'{sys.platform} is not supported :( try running in json-only mode with the -j flag')
        sys.exit(1)

    return os.path.join(root_directory, subdir)


def pretty_path(path: str) -> str:
    relpath = os.path.relpath(path, root_directory)
    abspath = os.path.abspath(path)
    cwdpath = os.path.relpath(path, os.getcwd())
    if len(cwdpath) <= min(len(relpath), len(abspath)):
        return cwdpath
    elif len(relpath) <= len(abspath):
        return relpath
    else:
        return abspath


def run_suitebro_parser(input_path: str, to_save: bool, output_path: str,
                        overwrite: bool = False) -> bool:
    exe_path = get_suitebro_path()
    process = Popen(f'\"{exe_path}\" {"to-save" if to_save else "to-json"} {"-!" if overwrite else ""}'
                    f' -i \"{input_path}\" -o \"{output_path}\"', stdout=PIPE, shell=True)
    (output, err) = process.communicate()
    for line in output.splitlines(False):
        info(line.decode('ascii'))

    exit_code = process.wait()

    if exit_code != 0:
        critical('Suitebro parser did not complete successfully!')
        return False

    success(f'Converted {pretty_path(input_path)} to {pretty_path(output_path)}')
    return True


def load_suitebro(filename: str, only_json: bool = False) -> Suitebro:
    abs_filepath = os.path.realpath(filename)
    in_dir = os.path.dirname(abs_filepath)
    json_output_path = os.path.join(in_dir, os.path.basename(abs_filepath) + ".json")

    if not only_json:
        run_suitebro_parser(abs_filepath, False, json_output_path, overwrite=True)

    info('Loading JSON file...')
    with open(json_output_path, 'r', encoding='utf-8') as fd:
        save_json = json.load(fd)

    save = Suitebro(os.path.basename(abs_filepath), in_dir, save_json)

    global _active_save
    _active_save = save

    return save


def save_suitebro(save: Suitebro, filename: str, only_json: bool = False):
    abs_filepath = os.path.realpath(filename)
    out_dir = os.path.dirname(abs_filepath)
    json_final_path = os.path.join(save.directory, f'{filename}.json')
    final_output_path = os.path.join(out_dir, f'{filename}')

    with open(json_final_path, 'w', encoding='utf-8') as fd:
        json.dump(save.to_dict(), fd, indent=2)

    # Finally run!
    if not only_json:
        run_suitebro_parser(json_final_path, True, final_output_path, overwrite=True)
