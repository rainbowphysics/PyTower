import difflib
import json
import logging
import sys
import uuid
import copy
import numpy as np

from .connections import ItemConnectionObject


def replace_guids(datadict, replacement_table):
    encoding = json.dumps(datadict)
    for target, replacement in replacement_table.items():
        encoding = encoding.replace(target, replacement)
    return json.loads(encoding)


class TowerObject:
    def __init__(self, item: dict | None = None, properties: dict | None = None):
        self.item = copy.deepcopy(item)
        self.properties = copy.deepcopy(properties)

        if self.item is not None and 'ItemConnections' not in self.item.keys():
            self.item['ItemConnections'] = json.loads('''{
              "ArrayProperty": {
                "StructProperty": {
                  "field_name": "ItemConnections",
                  "value_type": "StructProperty",
                  "struct_type": "ItemConnectionData",
                  "values": []
                }
              }
            }''')

    def get_name(self) -> str:
        return self.item['name']

    def get_custom_name(self) -> str:
        return self.item['properties']['ItemCustomName']['NameProperty']

    def matches_name(self, name) -> bool:
        name = name.casefold()
        return self.get_name() == name or self.get_custom_name().casefold() == name

    def get_group_id(self) -> int:
        return self.item['properties']['GroupID']['IntProperty']

    def copy(self) -> 'TowerObject':
        copied = TowerObject(item=self.item, properties=self.properties)
        if copied.item is not None:
            copied.item['guid'] = str(uuid.uuid4()).upper()
        return copied

    @staticmethod
    def copy_group(group: list) -> list['TowerObject']:
        # First pass: new guids and setup replacement table
        replacement_table = {}
        copies = [None] * len(group)
        for x, obj in enumerate(group):
            if obj.item is not None:
                old_guid = obj.item['guid']

            copied = obj.copy()

            if obj.item is not None:
                new_guid = copied.item['guid']
                replacement_table[old_guid] = new_guid

            copies[x] = copied

        # Second pass: replace any references to old guids with new guids
        for obj in copies:
            obj.item = replace_guids(obj.item, replacement_table)
            obj.properties = replace_guids(obj.properties, replacement_table)

        return copies

    def _get_xyz_attr(self, name: str) -> np.ndarray | None:
        if self.item is None:
            return None
        xyz = self.item[name]
        return np.array([xyz['x'], xyz['y'], xyz['z']])

    def _set_xyz_attr(self, name: str, value: np.ndarray):
        if self.item is None:
            logging.warning(f'Attempted to set {name} on a property-only object!')
            return

        pos = self.item[name]
        pos['x'] = value[0]
        pos['y'] = value[1]
        pos['z'] = value[2]

    @property
    def position(self) -> np.ndarray | None:
        return self._get_xyz_attr('position')

    @position.setter
    def position(self, value: np.ndarray):
        self._set_xyz_attr('position', value)

    @property
    def rotation(self) -> np.ndarray | None:
        return self._get_xyz_attr('rotation')

    @rotation.setter
    def rotation(self, value: np.ndarray):
        self._set_xyz_attr('rotation', value)

    @property
    def scale(self) -> np.ndarray | None:
        return self._get_xyz_attr('scale')

    @scale.setter
    def scale(self, value: np.ndarray):
        self._set_xyz_attr('scale', value)

    def add_connection(self, con: ItemConnectionObject):
        connections = self.item['ItemConnections']['ArrayProperty']['StructProperty']['values']
        connections += con.to_dict()
        self.properties['ItemConnections'] = self.item['ItemConnections']

    def get_connections(self) -> list[ItemConnectionObject]:
        cons = []
        for data in self.item['ItemConnections']['ArrayProperty']['StructProperty']['values']:
            cons.append(ItemConnectionObject(data))

        return cons

    def set_connections(self, cons: list[ItemConnectionObject]):
        self.item['ItemConnections']['ArrayProperty']['StructProperty']['values'] \
            = list(map(lambda con: con.to_dict(), cons))

    def __lt__(self, other):
        if not isinstance(other, TowerObject):
            return False

        if self.item is None and other.item is None:
            # CondoWeather needs to always be first, followed by CondoSettingsManager, then Ultra_Dynamic_Sky?
            if self.properties['name'].startswith('CondoWeather'):
                return True
            elif self.properties['name'].startswith('CondoSettingsManager'):
                return not other.properties['name'].startswith('CondoWeather')
            elif self.properties['name'].startswith('Ultra_Dynamic_Sky'):
                return (not other.properties['name'].startswith('CondoWeather')) and \
                    (not other.properties['name'].startswith('CondoSettingsManager'))

            return self.properties['name'] < other.properties['name']

        if self.item is None:
            return True

        if other.item is None:
            return False

        return self.item['name'] < other.item['name']

    def __repl__(self):
        return f'TowerObject({self.item}, {self.properties})'

    def __str__(self):
        return self.__repl__()


class Suitebro:
    def __init__(self, data: dict):
        self.data: dict = data

        # Parse objects
        prop_section = self.data['properties']
        item_section = self.data['items']
        self.objects: list[TowerObject | None] = [None] * len(prop_section)

        item_idx = 0
        for x in range(len(prop_section)):
            p = prop_section[x]
            i = item_section[item_idx]
            if p['name'].startswith(i['name']):
                self.objects[x] = TowerObject(item=i, properties=p)
                item_idx += 1
            else:
                self.objects[x] = TowerObject(item=None, properties=p)

    def add_object(self, obj):
        self.objects += [obj]

    def add_objects(self, objs):
        self.objects += objs

    def find_item(self, name: str) -> TowerObject | None:
        for obj in self.objects:
            if obj.matches_name(name):
                return obj
        return None

    # Returns all non-property TowerObjects
    def items(self) -> list[TowerObject]:
        return [obj for obj in self.objects if obj.item is not None]

    # Convert item list back into a dict
    def to_dict(self):
        new_dict = {}
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
