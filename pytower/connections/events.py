from ..object import TowerObject
from .connections import ItemConnectionObject, ItemConnectionData


class Event:
    _parent: TowerObject
    _event_name: str

    def __init__(self, parent: TowerObject, listener_event_name: str):
        self._parent = parent
        self._event_name = listener_event_name

    def connect(self, obj: TowerObject, event_name: str, delay: float = 0.0, data: ItemConnectionData | None = None):
        data_dict = {'Str': {'value': data.data}} if data is not None else None
        data_type = str(data.data_type) if data is not None else None

        con = ItemConnectionObject(guid=obj.guid, event_name=event_name, delay=delay, listener_event=self._event_name,
                                   datatype=data_type, data=data_dict)
        self._parent.add_connection(con)