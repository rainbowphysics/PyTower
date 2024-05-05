import copy
import json
import logging
import typing
import uuid

import numpy as np

from . import tower
from .connections import ItemConnectionObject

ITEMCONNECTIONS_DEFAULT = json.loads('''{
              "Array": {
                "array_type": "StructProperty",
                "value": {
                  "Struct": {
                    "_type": "ItemConnections",
                    "name": "StructProperty",
                    "struct_type": {
                      "Struct": "ItemConnectionData"
                    },
                    "id": "00000000-0000-0000-0000-000000000000",
                    "value": []
                  }
                } 
              }
            }''')


class TowerObject:
    def __init__(self, item: dict | None = None, properties: dict | None = None, nocopy: bool = False):
        if nocopy:
            self.item = item
            self.properties = properties
        else:
            self.item = copy.deepcopy(item)
            self.properties = copy.deepcopy(properties)

    def is_canvas(self) -> bool:
        if self.item is None:
            return False

        item_props = self.item['properties']
        return self.get_name().startswith('Canvas') or 'SurfaceMaterial' in item_props or 'URL' in item_props

    def get_name(self) -> str:
        if self.item is None:
            return self.properties['name']
        return self.item['name']

    def get_custom_name(self) -> str:
        if self.item is None or 'ItemCustomName' not in self.item['properties']:
            return ''
        return self.item['properties']['ItemCustomName']['Name']['value']

    def matches_name(self, name) -> bool:
        name = name.casefold()
        return self.get_name().casefold() == name or self.get_custom_name().casefold() == name

    def group_id(self) -> int:
        if self.item is None or 'GroupID' not in self.item['properties']:
            return -1
        return self.item['properties']['GroupID']['Int']['value']

    def set_group_id(self, group_id: int):
        self.item['properties']['GroupID'] = {'Int': {'value': group_id}}
        if self.properties is not None:
            self.properties['properties']['GroupID'] = {'Int': {'value': group_id}}

    # Removes group info from self
    def ungroup(self):
        if self.item is not None and 'GroupID' in self.item['properties']:
            del self.item['properties']['GroupID']

            if self.properties is not None:
                del self.properties['properties']['GroupID']

    def copy(self) -> 'TowerObject':
        copied = TowerObject(item=self.item, properties=self.properties)
        if copied.item is not None:
            copied.item['guid'] = str(uuid.uuid4()).lower()
        return copied

    def guid(self) -> str:
        return self.item['guid']

    def _get_xyz_attr(self, name: str) -> np.ndarray | None:
        if self.item is None:
            return None
        xyz = self.item[name]
        return np.array([xyz['x'], xyz['y'], xyz['z']])

    def _set_xyz_attr(self, name: str, value: np.ndarray):
        if self.item is None:
            logging.warning(f'Attempted to xyz set {name} on a property-only object!')
            return

        pos = self.item[name]
        pos['x'] = value[0]
        pos['y'] = value[1]
        pos['z'] = value[2]

    def _get_xyzw_attr(self, name: str) -> np.ndarray | None:
        if self.item is None:
            return None
        xyz = self.item[name]
        return np.array([xyz['x'], xyz['y'], xyz['z'], xyz['w']])

    def _set_xyzw_attr(self, name: str, value: np.ndarray):
        if self.item is None:
            logging.warning(f'Attempted to xyzw set {name} on a property-only object!')
            return

        pos = self.item[name]
        pos['x'] = value[0]
        pos['y'] = value[1]
        pos['z'] = value[2]
        pos['w'] = value[3]

    @property
    def position(self) -> np.ndarray | None:
        return self._get_xyz_attr('position')

    @position.setter
    def position(self, value: np.ndarray):
        self._set_xyz_attr('position', value)

    @property
    def rotation(self) -> np.ndarray | None:
        return self._get_xyzw_attr('rotation')

    @rotation.setter
    def rotation(self, value: np.ndarray):
        self._set_xyzw_attr('rotation', value)

    @property
    def scale(self) -> np.ndarray | None:
        return self._get_xyz_attr('scale')

    @scale.setter
    def scale(self, value: np.ndarray):
        self._set_xyz_attr('scale', value)

        if self.properties:
            props = self.properties['properties']

            if 'WorldScale' in props:
                props['WorldScale']['Struct']['value']['Vector']['x'] = value[0]
                props['WorldScale']['Struct']['value']['Vector']['y'] = value[1]
                props['WorldScale']['Struct']['value']['Vector']['z'] = value[2]

                self.item['properties']['WorldScale'] = props['WorldScale']

            if ('RespawnLocation' in props and 'properties' in self.item
                    and 'RespawnLocation' in self.item['properties']):
                scale3d_data = props['RespawnLocation']['Struct']['value']['Struct']['Scale3D']
                scale3d = scale3d_data['Struct']['value']['Vector']
                scale3d['x'] = value[0]
                scale3d['y'] = value[1]
                scale3d['z'] = value[2]

                self.item['properties']['RespawnLocation'] = props['RespawnLocation']

    def _check_connetions(self):
        if self.item is not None and 'ItemConnections' not in self.item.keys():
            self.item['ItemConnections'] = copy.deepcopy(ITEMCONNECTIONS_DEFAULT)

    def add_connection(self, con: ItemConnectionObject):
        assert self.item is not None
        self._check_connetions()

        connections = self.item['properties']['ItemConnections']['Array']['value']['Struct']['value']
        connections.append(con.to_dict())

        if self.properties is not None:
            self.properties['properties']['ItemConnections'] = self.item['properties']['ItemConnections']

    def get_connections(self) -> list[ItemConnectionObject]:
        assert self.item is not None
        self._check_connetions()

        cons = []
        for data in self.item['properties']['ItemConnections']['Array']['value']['Struct']['value']:
            cons.append(ItemConnectionObject(data))

        return cons

    def set_connections(self, cons: list[ItemConnectionObject]):
        assert self.item is not None
        self._check_connetions()

        self.item['properties']['ItemConnections']['Array']['value']['Struct']['value'] \
            = list(map(lambda con: con.to_dict(), cons))

        if self.properties is not None:
            self.properties['properties']['ItemConnections'] = self.item['properties']['ItemConnections']

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
