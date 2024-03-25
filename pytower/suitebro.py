import json
import uuid
import copy

def replace_guids(datadict, replacement_table):
    encoding = json.dumps(datadict)
    for target, replacement in replacement_table.items():
        encoding.replace(target, replacement)
    return json.loads(encoding)


def run_if_not_none(func, data):
    if data is not None:
        func(data)


class ItemConnectionObject:
    def __init__(self, datadict=None, guid=None, event_name=None, delay=None, listener_event=None, datatype=None,
                 data=None):
        if datadict is not None:
            self.data = datadict
            return

        # Load in dictionary template with default values
        self.data = json.loads('''{
                  "struct_type": "ItemConnectionData",
                  "value": {
                    "Item": {
                      "StructProperty": {
                        "struct_type": "GUID",
                        "value": null
                      }
                    },
                    "EventName": {
                      "NameProperty": null
                    },
                    "Delay": {
                      "FloatProperty": 0.0
                    },
                    "ListenerEventName": {
                      "NameProperty": null
                    },
                    "DataType": {
                      "EnumProperty": {
                        "enum_type": "FItemDataType",
                        "value": "FItemDataType::NONE"
                      }
                    },
                    "Data": {
                      "StrProperty": ""
                    }
                  }
                }''')

        setter_pairs = [(self.set_item_guid, guid),
                        (self.set_event_name, event_name),
                        (self.set_delay, delay),
                        (self.set_listener_event_name, listener_event),
                        (self.set_datatype, datatype),
                        (self.set_data, data)
                        ]
        for setter, entry in setter_pairs:
            run_if_not_none(setter, entry)

    # Returns connected item GUID
    def get_item_guid(self) -> str:
        return self.data['value']['Item']['StructProperty']['value']

    def set_item_guid(self, guid: str):
        self.data['value']['Item']['StructProperty']['value'] = guid

    # Returns targeted event on item
    def get_event_name(self) -> str:
        return self.data['value']['EventName']['NameProperty']

    def set_event_name(self, name: str):
        self.data['value']['EventName']['NameProperty'] = name

    # Returns time delay in seconds
    def get_delay(self) -> float:
        return self.data['value']['Delay']['FloatProperty']

    def set_delay(self, delay: float):
        self.data['value']['Delay']['FloatProperty'] = delay

    # Returns evnet being listened to
    def get_listener_event_name(self) -> str:
        return self.data['value']['Item']['StructProperty']['value']

    def set_listener_event_name(self, name: str):
        self.data['value']['Item']['StructProperty']['value'] = name

    # Returns datatype of attached data
    def get_datatype(self) -> dict:
        return self.data['value']['DataType']

    def set_datatype(self, datatype: dict):
        self.data['value']['DataType'] = datatype

    # Returns datatype of attached data
    def get_data(self) -> dict:
        return self.data['value']['Data']

    def set_data(self, data: dict):
        self.data['value']['Data'] = data

    def get_dict(self) -> dict:
        return self.data

    def set_dict(self, data):
        self.data = data

    def to_dict(self) -> dict:
        return copy.deepcopy(self.data)

    # Needed to call dict(...) on objects of this class type
    def __iter__(self):
        for k, v in self.data:
            yield k, v


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

    def copy(self) -> 'TowerObject':
        copied = TowerObject(item=self.item, properties=self.properties)
        if copied.item is not None:
            copied.item['guid'] = str(uuid.uuid4()).upper()
        return copied

    def get_name(self) -> str:
        return self.item['name']

    def get_custom_name(self) -> str:
        return self.item['properties']['ItemCustomName']['NameProperty']

    def matches_name(self, name) -> bool:
        name = name.casefold()
        return self.get_name() == name or self.get_custom_name().casefold() == name

    def get_group_id(self) -> int:
        return self.item['properties']['GroupID']['IntProperty']

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
            replace_guids(obj.item, replacement_table)
            replace_guids(obj.properties, replacement_table)

        return copies

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
