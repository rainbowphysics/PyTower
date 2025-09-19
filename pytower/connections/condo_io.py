from .connections import ItemConnectionData
from .events import Event
from ..object import TowerObject

class Relay:
    obj: TowerObject
    event: Event

    def __init__(self, obj: TowerObject):
        self.obj = obj
        self.event = Event(self.obj, 'OnFired')

    def connect(self, obj: TowerObject, event_name: str, delay: float = 0.0, data: ItemConnectionData | None = None):
        self.event.connect(obj, event_name, delay=delay, data=data)