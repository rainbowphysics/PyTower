import copy
from typing import Any, Callable
from ..util import run_if_not_none

CONNECTION_DEFAULT: dict[str, Any] = {
    "Struct": {
        "Item": {
            "Struct": {
                "value": {
                    "Guid": None
                },
                "struct_type": "Guid",
                "struct_id": "00000000-0000-0000-0000-000000000000"
            }
        },
        "EventName": {
            "Name": {
                "value": None
            }
        },
        "Delay": {
            "Float": {
                "value": 0.0
            }
        },
        "ListenerEventName": {
            "Name": {
                "value": None
            }
        },
        "DataType": {
            "Enum": {
                "enum_type": "FItemDataType",
                "value": "FItemDataType::NONE"
            }
        },
        "Data": {
            "Str": {
                "value": ""
            }
        }
    }
}


class ItemConnectionObject:
    data: dict[str, Any]

    def __init__(self, datadict: dict[str, Any] | None = None, guid: str | None = None, event_name: str | None = None,
                 delay: float | None = None, listener_event: str | None = None, datatype: dict[str, Any] | None = None,
                 data: dict[str, Any] | None = None):
        if datadict is not None:
            self.data = datadict
            return

        # Load in dictionary template with default values
        self.data = copy.deepcopy(CONNECTION_DEFAULT)

        setter_pairs: list[tuple[Callable[[Any], None], Any]] = [
            (self.set_item_guid, guid),
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
        return self.data['Struct']['Item']['value']['Struct']['value']['Guid']

    def set_item_guid(self, guid: str):
        self.data['Struct']['Item']['value']['Struct']['value']['Guid'] = guid

    # Returns targeted event on item
    def get_event_name(self) -> str:
        return self.data['Struct']['EventName']['Name']['value']

    def set_event_name(self, name: str):
        self.data['Struct']['EventName']['Name']['value'] = name

    # Returns time delay in seconds
    def get_delay(self) -> float:
        return self.data['Struct']['Delay']['Float']['value']

    def set_delay(self, delay: float):
        self.data['Struct']['Delay']['Float']['value'] = delay

    # Returns evnet being listened to
    def get_listener_event_name(self) -> str:
        return self.data['Struct']['ListenerEventName']['Name']['value']

    def set_listener_event_name(self, name: str):
        self.data['Struct']['ListenerEventName']['Name']['value'] = name

    # Returns datatype of attached data
    def get_datatype(self) -> dict[str, Any]:
        return self.data['Struct']['DataType']['Enum']['value']

    def set_datatype(self, datatype: dict[str, Any]):
        self.data['Struct']['DataType']['Enum']['value'] = datatype

    # Returns datatype of attached data
    def get_data(self) -> dict[str, Any]:
        return self.data['Struct']['Data']

    def set_data(self, data: dict[str, Any]):
        self.data['Struct']['Data'] = data

    def get_dict(self) -> dict[str, Any]:
        return self.data

    def set_dict(self, data: dict[str, Any]):
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self.data)

    # Needed to call dict(...) on objects of this class type
    def __iter__(self):
        for k, v in self.data:
            yield k, v
