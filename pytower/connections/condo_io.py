from dataclasses import dataclass

from .connections import ItemConnectionData
from .events import Event
from ..object import TowerObject


class CondoIO:
    events: list[Event]

    def __init__(self, obj: TowerObject, *event_names: str):
        self.events = []
        for event_name in event_names:
            self.events.append(Event(obj, event_name))

    def connect(self, obj: TowerObject, event_name: str, delay: float = 0.0, data: ItemConnectionData | None = None):
        assert len(self.events) == 0

        self.events[0].connect(obj, event_name, delay=delay, data=data)

    def connect_to_event(self, listener_event: str, obj: TowerObject, event_name: str, delay: float = 0.0,
                      data: ItemConnectionData | None = None):
        for event in self.events:
            if event.event_name == listener_event:
                event.connect(obj, event_name, delay=delay, data=data)

        raise ValueError(f'Failed to find event with name {listener_event}')

    def get_event(self, name: str) -> Event | None:
        for event in self.events:
            if event.event_name == name:
                return event
        return None

    def __getattr__(self, name: str):
        return self.get_event(name)


class Button(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnPressed')

class Counter(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnReachedMax', 'OnReachedMin', 'OnChanged')

class Clock(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnHourPassed', 'OnMinutePassed', 'OnSecondPassed', 'On12HourPassed')

class GameWorldEvents(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnRoundStart', 'OnRoundEnd', 'OnMatchStart', 'OnMatchEnd') #TODO implement rest

class HitTargetVolume(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnDeath', 'OnHurt')

class LightSwitch(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnSwitchOn', 'OnSwitchOff')

class Mover(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnStart', 'OnEnd')

class PhysicsSlot(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnSlot')

class PlayerEvents(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnPlayerJoined', 'OnPlayerLeft', 'OnPlayerSpawned', 'OnPlayerKilled')

class Random(CondoIO):
    def __init__(self, obj: TowerObject):
        result_names = [f'OnResult{x+1}' for x in range(128)]
        super().__init__(obj, 'OnFired', 'OnAllPicked', *result_names)

class Relay(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnFired')

class Timer(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnTimerComplete', 'OnTimerStarted', 'OnTimerPaused', 'OnTimerResumed',
                         'OnTimerStopped', 'OnTimerChanged')

class Toggle(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'On', 'Off')

class TriggerVolume(CondoIO):
    def __init__(self, obj: TowerObject):
        super().__init__(obj, 'OnTrigger', 'OnLeaveTrigger')