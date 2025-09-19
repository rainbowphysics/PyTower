from dataclasses import dataclass

from .connections import ItemConnectionData
from .events import Event
from ..object import TowerObject

@dataclass
class CondoIO:
    events: list[Event]

    def _connect_idx(self, idx: int, obj: TowerObject, event_name: str, delay: float = 0.0,
                     data: ItemConnectionData | None = None):
        self.events[idx].connect(obj, event_name, delay=delay, data=data)

    def connect(self, obj: TowerObject, event_name: str, delay: float = 0.0, data: ItemConnectionData | None = None):
        assert len(self.events) == 0

        self._connect_idx(0, obj, event_name, delay=delay, data=data)

    def connect_to_event(self, listener_event: str, obj: TowerObject, event_name: str, delay: float = 0.0,
                      data: ItemConnectionData | None = None):
        for x, event in enumerate(self.events):
            if event.event_name == listener_event:
                self._connect_idx(x, obj, event_name, delay=delay, data=data)

class Relay(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__([Event(obj, 'OnFired')])