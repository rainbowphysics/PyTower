from __future__ import annotations
import copy
import re
import uuid
from typing import Any, cast, TypeAlias

from deprecated.sphinx import deprecated
import numpy as np

from .connections import ItemConnectionObject
from .connections.connections import ItemConnectionData
from .util import XYZ, XYZW, not_none, xyz

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
_fv = _v('Float')
_bv = _v('Bool')
_stv = _v('Str')

Spec: TypeAlias = list[str]


def spec_keys(spec: str) -> Spec:
    return spec.split('.')


def _exists(data, spec: Spec):
    if data is None:
        return False

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
_ITEM_METADATA_SCALE_SPEC = spec_keys(f'properties.ItemMetadataScale.{_fv}')

_URL_SPEC = spec_keys(f'properties.URL.{_stv}')
# _SURFACE_MAT_SPEC = spec_keys(f'properties.SurfaceMaterial.{_stv}')

# UUID4 regex pattern
_UUID_PATTERN = re.compile('^' + '-'.join([fr'[\da-f]{{{d}}}' for d in [8, 4, 4, 4, 12]]) + '$')


def _preprocess_path(path: Spec | str) -> Spec:
    if isinstance(path, str):
        path = spec_keys(path)

    if path[0] != 'properties':
        path = ['properties'] + path

    return path

def _preprocess_value(value: Any) -> Any:
    if isinstance(value, XYZ):
        value = value.to_dict()

    return value

class TowerObject:
    """Represents an object appearing in the Suitebro file. This includes all the sections of the object."""

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

    def get_property(self, path: Spec | str) -> Any | None:
        """
        Gets property value

        Args:
            path: Either a list of string keys or a period-separated string representing the path to take through
                the dictionary. For example, "properties.ItemCustomName.Name.value" and ["properties", "ItemCustomName",
                "Name", "value"]

        Returns:
            Value at path or None
        """
        if isinstance(path, str):
            path = spec_keys(path)

        if path[0] != 'properties':
            path = ['properties'] + path

        if self.properties is not None:
            prelim_result = get_in(path, self.properties, default=None)
        else:
            prelim_result = get_in(path, self.item, default=None)

        if not isinstance(prelim_result, dict):
            return prelim_result

        # Walk the dict to try to figure out what this is
        # Case 1: we were given a field without the Type.value suffix
        while len(prelim_result) == 1 or 'value' in prelim_result:
            if 'value' in prelim_result:
                prelim_result = prelim_result['value']
            else:
                prelim_result = prelim_result.pop(prelim_result.keys()[0])

        if not isinstance(prelim_result, dict):
            return prelim_result

        # Case 2: value is Vector or Label or TODO Struct or array
        if len(prelim_result) == 1 and 'Vector' in prelim_result:
            prelim_result = prelim_result['Vector']
        elif len(prelim_result) == 1 and 'Label' in prelim_result:
            return prelim_result['Label']

        # Check if we're in a Vector
        if isinstance(prelim_result, dict) and 'x' in prelim_result and 'y' in prelim_result and 'z' in prelim_result:
            vector_data = [prelim_result['x'], prelim_result['y'], prelim_result['z']]
            if 'w' in prelim_result:
                vector_data.append(prelim_result['w'])
            return xyz(vector_data)

        # At this point we give up and just return a dict
        return prelim_result

    def set_property(self, path: Spec | str, value: Any):
        """
        Sets property in both item and properties sections

        Args:
            path: Either a list of string keys or a period-separated string representing the path to take through
                the dictionary. For example, "properties.ItemCustomName.Name.value" and ["properties", "ItemCustomName",
                "Name", "value"]

            value: Value to set
        """
        assert self.item is not None

        spec = _preprocess_path(path)
        value = _preprocess_value(value)

        self.item = update_in(self.item, spec, lambda _: value)
        if self.properties is not None:
            self.set_meta_property(spec, value)

    def set_meta_property(self, path: Spec | str, value: Any):
        """
        Sets property only the properties section

        Args:
            path: Either a list of string keys or a period-separated string representing the path to take through
                the dictionary. For example, "properties.ItemCustomName.Name.value" and ["properties", "ItemCustomName",
                "Name", "value"]

            value: Value to set
        """
        assert self.properties is not None

        spec = _preprocess_path(path)
        value = _preprocess_value(value)

        self.properties = update_in(self.properties, spec, lambda _: value)

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
        """Name used by Tower Unite internally"""
        return self.item['name'] if self.item is not None else not_none(self.properties)['name']

    @deprecated(reason='Use TowerObject.custom_name instead', version='0.3.0')
    def get_custom_name(self) -> str:
        return self.custom_name

    @property
    def custom_name(self) -> str:
        """Custom name set by Tower Unite player"""
        return get_in(_CUSTOM_NAME_SPEC, self.item, default='')

    @custom_name.setter
    def custom_name(self, value: str):
        self.set_property(_CUSTOM_NAME_SPEC, value)

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
        self.set_property(_GROUP_ID_SPEC, value)

    def ungroup(self):
        """Clears the group info attached to this object, effectively un-grouping it"""
        if _exists(self.item, _GROUP_ID_SPEC):
            del self.item['properties']['GroupID']

        if self.properties is not None:
            self.set_meta_property(_GROUP_ID_SPEC, -1)

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

        return xyz(vector)

    def _set_xyz(self, spec: Spec, value: XYZ, meta: bool = False):
        vector_dict = value.to_dict()
        self.item = update_in(self.item, spec, lambda _: vector_dict)

        if meta and self.properties is not None:
            self.properties = update_in(self.properties, spec, lambda _: vector_dict)

    @property
    def metadata_scale(self) -> float:
        """Metadata scale (used by some workshop items)"""
        return get_in(_ITEM_METADATA_SCALE_SPEC, self.item, default=1.0)

    # region position
    @property
    def position(self) -> XYZ | None:
        """World position"""
        return self._get_xyz(_POS_SPEC) if self.item is not None else None

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
        return self._get_xyz(_ROT_SPEC) if self.item is not None else None

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
        return self._get_xyz(_SCALE_SPEC) if self.item is not None else None

    @scale.setter
    def scale(self, value: XYZ):
        self._set_xyz(_SCALE_SPEC, value)

        if not _exists(self.item, spec_keys('properties.WorldScale')) and self.item is not None:
            self.item = update_in(self.item, spec_keys('properties.WorldScale.Struct.struct_type'), lambda _: 'Vector')
            self.item = update_in(self.item, spec_keys('properties.WorldScale.Struct.struct_id'),
                                  lambda _: '00000000-0000-0000-0000-000000000000')
        if not _exists(self.properties, spec_keys('properties.WorldScale')) and self.properties is not None:
            self.properties = update_in(self.properties, spec_keys('properties.WorldScale.Struct.struct_type'),
                                        lambda _: 'Vector')
            self.properties = update_in(self.properties, spec_keys('properties.WorldScale.Struct.struct_id'),
                                        lambda _: '00000000-0000-0000-0000-000000000000')

        self._set_xyz(_WORLD_SCALE_SPEC, value / self.metadata_scale, meta=True)

        if _exists(self.item, _RESPAWN_SPEC):
            self._set_xyz(_RESPAWN_SCALE3D_SPEC, value / self.metadata_scale, meta=True)

    # endregion scale

    def compress(self):
        if self.properties is None or self.item is None:
            return

        prop_entries = copy.copy(set(self.properties['properties'].keys()))
        for prop in prop_entries:
            if prop not in self.item['properties']:
                del self.properties['properties'][prop]

    @property
    def url(self) -> str | None:
        if not self.is_canvas():
            return None

        return get_in(_URL_SPEC, self.item, no_default=True)

    @url.setter
    def url(self, value: str):
        self.set_property(_URL_SPEC, value)

    def _check_connetions(self):
        if not _exists(self.item, _ITEM_CONNECTIONS_SPEC):
            self.item = update_in(self.item, _ITEM_CONNECTIONS_PARENT_SPEC,
                                  lambda _: copy.deepcopy(ITEMCONNECTIONS_DEFAULT))
        
        if self.properties is not None and not _exists(self.properties, _ITEM_CONNECTIONS_SPEC):
            self.properties = update_in(self.properties, _ITEM_CONNECTIONS_PARENT_SPEC,
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
        self.set_property(_ITEM_CONNECTIONS_SPEC, connections)

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
        self.set_property(_ITEM_CONNECTIONS_SPEC, cons_list)

    def connect_to(self, listener_event_name: str, other: TowerObject, event_name: str, delay: float = 0.0,
                   data: ItemConnectionData | None = None):
        """
        Connect this object to another object

        Args:
            listener_event_name: The name of the listener event to connect to (for example, "OnFired")
            other: The other object to connect to
            event_name: The name of the event on this object to connect from
            delay: The delay in seconds
            data: The optional data to use for this event
        """
        data_dict = {'Str': {'value': data.data}} if data is not None else None
        data_type = str(data.data_type) if data is not None else None

        con = ItemConnectionObject(guid=self.guid, event_name=event_name, delay=delay,
                                   listener_event=listener_event_name, datatype=data_type, data=data_dict)

        other.add_connection(con)

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

        if self.item['name'] != other.item['name']:
            return self.item['name'] < other.item['name']

        if self.item['name'].startswith('BaseWorkshopItem'):
            self_workshop_file = self.item['actors'][0]['properties']['WorkshopFile']['Struct']['value']['WorkshopFile']
            other_workshop_file = other.item['actors'][0]['properties']['WorkshopFile']['Struct']['value'][
                'WorkshopFile']

            return self_workshop_file < other_workshop_file

        return False

    def __repl__(self):
        return f'{__class__.__name__}({self.item}, {self.properties})'

    def __str__(self):
        return self.__repl__()

    @staticmethod
    def deserialize_objects(data: dict) -> list[TowerObject]:
        # Parse objects
        prop_section = data['properties']
        item_section = data['items']
        num_props = len(prop_section)
        num_items = len(item_section)
        objects: list[TowerObject] = [None] * (num_items + num_props)  # type: ignore[assignment]

        # First get all names present in properties to determine item-only objects. Except for property-only metadata
        #  objects, every property name is <SOME ITEM NAME>_C_###, where ### is the index within the item-type grouping
        prop_names = set[str]()
        for prop_data in prop_section:
            name: str = prop_data['name']
            try:
                name_end = name.rindex('_C_')
                prop_names.add(name[:name_end])
            except ValueError:
                continue

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

            if i is not None and i['name'] == 'None':
                # Skip the "None" object left behind by spline anchor points
                item_idx += 1
                continue

            if i is not None and i['name'] not in prop_names:
                objects[x] = TowerObject(item=i, properties=None, nocopy=True)
                item_idx += 1
            elif i is not None and p is not None and p['name'].startswith(i['name']):
                objects[x] = TowerObject(item=i, properties=p, nocopy=True)
                item_idx += 1
                prop_idx += 1
            elif p is not None:
                objects[x] = TowerObject(item=None, properties=p, nocopy=True)
                prop_idx += 1

            x += 1

        # Now cull Nones at the end of array
        if None in objects:  # type: ignore[read]
            size = objects.index(None)  # type: ignore[read]
            objects = objects[:size]

        return objects