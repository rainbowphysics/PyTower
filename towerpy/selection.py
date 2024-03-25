from .suitebro import TowerObject

from abc import ABC, abstractmethod
import re


class Selection(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def select(self, everything: list[TowerObject]) -> list[TowerObject]:
        pass


class NameSelection(Selection):
    def __init__(self, select_name):
        super().__init__('NameSelection')
        self.select_name = select_name.casefold()

    def select(self, everything: [TowerObject]) -> [TowerObject]:
        return [obj for obj in everything if obj.matches_name(self.select_name)]


class CustomNameSelection(Selection):
    def __init__(self, select_name):
        super().__init__('CustomNameSelection')
        self.select_name = select_name.casefold()

    def select(self, everything: [TowerObject]) -> [TowerObject]:
        return [obj for obj in everything if obj.get_custom_name().casefold() == self.select_name]


class ObjectNameSelection(Selection):
    def __init__(self, select_name):
        super().__init__('ObjectNameSelection')
        self.select_name = select_name.casefold()

    def select(self, everything: [TowerObject]) -> [TowerObject]:
        return [obj for obj in everything if obj.get_name().casefold() == self.select_name]


class RegexSelection(Selection):
    def __init__(self, pattern):
        super().__init__('RegexSelection')
        self.pattern = re.compile(pattern)

    def select(self, everything: list[TowerObject]) -> list[TowerObject]:
        return [obj for obj in everything if self.pattern.match(obj.get_name())
                or self.pattern.match(obj.get_custom_name())]


class GroupSelection(Selection):
    def __init__(self, group_id):
        super().__init__('GroupSelection')
        self.group_id = group_id

    def select(self, everything: list[TowerObject]) -> list[TowerObject]:
        return [obj for obj in everything if obj.get_group_id() == self.group_id]


class ItemSelection(Selection):
    def __init__(self):
        super().__init__('ItemSelection')

    def select(self, everything: list[TowerObject]) -> list[TowerObject]:
        return [obj for obj in everything if obj.item is not None]
