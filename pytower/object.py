from __future__ import annotations
import copy
import re
import uuid
from typing import Any, cast

from deprecated.sphinx import deprecated
import numpy as np

from .connections import ItemConnectionObject
from .util import XYZ, XYZW, not_none

from toolz import get_in, update_in

ITEMCONNECTIONS_DEFAULT: dict[str, Any] = {
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
}


def _v(name: str):
    return f'{name}.value'


def _s(name: str):
    return f'Struct.{name}'


_sv = _v('Struct')
_iv = _v('Int')
_nv = _v('Name')
_av = _v('Array')

Spec = list[str]


def spec_keys(spec: str) -> Spec:
    return spec.split('.')


def _exists(data, spec: Spec):
    try:
        # Attempt to access the path
        get_in(spec, data, no_default=True)
        return True
    except (KeyError, IndexError):
        # Path does not exist
        return False


_GROUP_ID_SPEC = spec_keys(f'properties.GroupID.{_iv}')
_CUSTOM_NAME_SPEC = spec_keys(f'properties.ItemCustomName.{_nv}')

_POS_SPEC = spec_keys('position')
_ROT_SPEC = spec_keys('rotation')
_SCALE_SPEC = spec_keys('scale')

_RESPAWN_SPEC = spec_keys('properties.RespawnLocation')
_RESPAWN_TRANSLATION_SPEC = spec_keys(f'properties.RespawnLocation.{_sv}.{_s("Translation")}.{_sv}.Vector')
_RESPAWN_ROTATION_SPEC = spec_keys(f'properties.RespawnLocation.{_sv}.{_s("Rotation")}.{_sv}.Quat')
_RESPAWN_SCALE3D_SPEC = spec_keys(f'properties.RespawnLocation.{_sv}.{_s("Scale3D")}.{_sv}.Vector')
_WORLD_SCALE_SPEC = spec_keys(f'properties.WorldScale.{_sv}.Vector')
_ITEM_CONNECTIONS_PARENT_SPEC = spec_keys(f'properties.ItemConnections')
_ITEM_CONNECTIONS_SPEC = spec_keys(f'properties.ItemConnections.{_av}.{_sv}')

# UUID4 regex pattern
_UUID_PATTERN = re.compile('^' + '-'.join([fr'[\da-f]{{{d}}}' for d in [8, 4, 4, 4, 12]]) + '$')


class TowerObject:
    """
    Represents an object appearing in the Suitebro file. This includes all the sections of the object.
    """

    def __init__(self, item: dict[str, Any] | None = None, properties: dict[str, Any] | None = None,
                 nocopy: bool = False):
        """
        Initializes TowerObject instance taking in uesave json data

        To ensure uniqueness, this assigns a new GUID to this object

        Args:
            item: The item section parsed, as parsed from tower-unite-suitebro
            properties: The properties section, as parsed from tower-unite-suitebro
            nocopy: If True, then do not deep-copy the item and properties dictionaries
        """
        # When nocopy true, just set item and properties for performance
        if nocopy:
            self.item = item
            self.properties = properties
            return

        # Deep copy dicts
        self.item = copy.deepcopy(item)
        self.properties = copy.deepcopy(properties)

        # Generate new UUID4
        if self.item is not None:
            self.guid = str(uuid.uuid4()).lower()

    def _set_property(self, path: Spec, value: Any):
        assert self.item is not None
        self.item = update_in(self.item, path, lambda _: value)
        if self.properties is not None:
            self._set_meta_property(path, value)

    def _set_meta_property(self, path: Spec, value: Any):
        assert self.properties is not None
        self.properties = update_in(self.properties, path, lambda _: value)

    def is_canvas(self) -> bool:
        """
        Returns:
            Whether object is a canvas object
        """
        if self.item is None:
            return False

        item_props = self.item['properties']
        return self.name.startswith('Canvas') or 'SurfaceMaterial' in item_props or 'URL' in item_props

    @deprecated(reason='Use TowerObject.name instead', version='0.3.0')
    def get_name(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """
        Name used by Tower Unite internally
        """
        return self.item['name'] if self.item is not None else not_none(self.properties)['name']

    @deprecated(reason='Use TowerObject.custom_name instead', version='0.3.0')
    def get_custom_name(self) -> str:
        return self.custom_name

    @property
    def custom_name(self) -> str:
        """
        Custom name set by Tower Unite player
        """
        return get_in(_CUSTOM_NAME_SPEC, self.item, default='')

    @custom_name.setter
    def custom_name(self, value: str):
        self._set_property(_CUSTOM_NAME_SPEC, value)

    def matches_name(self, name: str) -> bool:
        """
        Determines if instance matches input name

        Args:
            name: Name to match against

        Returns:
            True if the input name matches name or custom_name, case-insensitive
        """
        name = name.casefold().strip()
        return self.name.strip().casefold() == name or self.custom_name.strip().casefold() == name

    @deprecated(reason='Assign to TowerObject.group_id instead', version='0.3.0')
    def set_group_id(self, group_id: int):
        self.group_id = group_id

    @property
    def group_id(self) -> int:
        """TowerObject's Group ID"""
        return get_in(_GROUP_ID_SPEC, self.item, default=-1)

    @group_id.setter
    def group_id(self, value: int):
        self._set_property(_GROUP_ID_SPEC, value)

    def ungroup(self):
        """
        Clears the group info attached to this object, effectively un-grouping it
        """
        if _exists(self.item, _GROUP_ID_SPEC):
            del self.item['properties']['GroupID']

        if self.properties is not None:
            self._set_meta_property(_GROUP_ID_SPEC, -1)

    def copy(self) -> TowerObject:
        """
        Creates a new TowerObject with the same item and properties as this one.

        Returns:
            Copy of this TowerObject instance
        """
        copied = TowerObject(item=self.item, properties=self.properties)
        return copied

    @property
    def guid(self) -> str:
        """TowerObject's GUID"""
        assert self.item is not None
        return self.item['guid']

    @guid.setter
    def guid(self, value: str):
        assert self.item is not None
        value = value.lower().strip()
        assert _UUID_PATTERN.match(value)
        self.item['guid'] = value

    def _get_xyz(self, spec: Spec, meta: bool = False):
        vec_data = get_in(spec, self.item if not meta else self.properties, no_default=True)
        vector = [vec_data['x'], vec_data['y'], vec_data['z']]
        if 'w' in vec_data:
            vector.append(vec_data['w'])
            return np.array(vector).view(XYZW)

        return np.array(vector).view(XYZ)

    def _set_xyz(self, spec: Spec, value: XYZ, meta: bool = False):
        vector_dict = value.to_dict()
        self.item = update_in(self.item, spec, lambda _: vector_dict)

        if meta:
            self.properties = update_in(self.properties, spec, lambda _: vector_dict)

    # region position
    @property
    def position(self) -> XYZ | None:
        """World position"""
        return self._get_xyz(_POS_SPEC)

    @position.setter
    def position(self, value: XYZ):
        self._set_xyz(_POS_SPEC, value)

        if _exists(self.item, _RESPAWN_SPEC):
            self._set_xyz(_RESPAWN_TRANSLATION_SPEC, value, meta=True)

    # endregion position

    # region rotation
    @property
    def rotation(self) -> XYZW | None:
        """Rotation quaternion"""
        return self._get_xyz(_ROT_SPEC)

    @rotation.setter
    def rotation(self, value: XYZW):
        self._set_xyz(_ROT_SPEC, value)

        if _exists(self.item, _RESPAWN_SPEC):
            self._set_xyz(_RESPAWN_ROTATION_SPEC, value, meta=True)

    # endregion rotation

    # region scale
    @property
    def scale(self) -> XYZ | None:
        """Local scale"""
        return self._get_xyz(_SCALE_SPEC)

    @scale.setter
    def scale(self, value: XYZ):
        self._set_xyz(_SCALE_SPEC, value)

        if _exists(self.item, _WORLD_SCALE_SPEC):
            self._set_xyz(_WORLD_SCALE_SPEC, value, meta=True)

        if _exists(self.item, _RESPAWN_SPEC):
            self._set_xyz(_RESPAWN_SCALE3D_SPEC, value, meta=True)

    # endregion scale

    def _check_connetions(self):
        if not _exists(self.item, _ITEM_CONNECTIONS_SPEC):
            self.item = update_in(self.item, _ITEM_CONNECTIONS_PARENT_SPEC,
                                  lambda _: copy.deepcopy(ITEMCONNECTIONS_DEFAULT))

    def add_connection(self, con: ItemConnectionObject):
        """
        Adds a connection to this object

        Args:
            con: The connection to add to this object
        """
        assert self.item is not None
        self._check_connetions()

        connections = get_in(_ITEM_CONNECTIONS_SPEC, self.item, no_default=True)
        connections.append(con.to_dict())
        self._set_property(_ITEM_CONNECTIONS_SPEC, connections)

    def get_connections(self) -> list[ItemConnectionObject]:
        """
        Returns:
            List of connections attached to this object
        """
        assert self.item is not None
        self._check_connetions()

        cons_list = list[ItemConnectionObject]()
        connections_data = get_in(_ITEM_CONNECTIONS_SPEC, self.item, no_default=True)
        for con_data in connections_data:
            cons_list.append(ItemConnectionObject(con_data))

        return cons_list

    def set_connections(self, cons: list[ItemConnectionObject]):
        """
        Set all the connections attached to this object. Useful when resetting/overriding connections

        Args:
            cons: List of connections to attach onto this object
        """
        assert self.item is not None
        self._check_connetions()
        cons_list = [con.to_dict() for con in cons]
        self._set_property(_ITEM_CONNECTIONS_SPEC, cons_list)

    def __lt__(self, other: Any):
        if not isinstance(other, TowerObject):
            return False

        if self.item is None and other.item is None:
            assert self.properties is not None
            assert other.properties is not None

            self_name = cast(str, self.properties['name'])
            other_name = cast(str, other.properties['name'])

            # CondoWeather needs to always be first, followed by CondoSettingsManager, then Ultra_Dynamic_Sky?
            if self_name.startswith('CondoWeather'):
                return True
            elif self_name.startswith('CondoSettingsManager'):
                return not other_name.startswith('CondoWeather')
            elif self_name.startswith('Ultra_Dynamic_Sky'):
                return not other_name.startswith('CondoWeather') and not other_name.startswith('CondoSettingsManager')

            return self_name < other_name

        if self.item is None:
            return True

        if other.item is None:
            return False

        return self.item['name'] < other.item['name']

    def __repl__(self):
        return f'{__class__.__name__}({self.item}, {self.properties})'

    def __str__(self):
        return self.__repl__()
