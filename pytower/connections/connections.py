import copy
import json
from pytower.util import run_if_not_none


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
        return self.data['value']['ListenerEventName']['NameProperty']

    def set_listener_event_name(self, name: str):
        self.data['value']['ListenerEventName']['NameProperty'] = name

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
