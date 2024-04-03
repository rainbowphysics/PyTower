import itertools

from .object import TowerObject

from abc import ABC, abstractmethod
import re


class Selection(set[TowerObject]):
    @staticmethod
    def _group_key(obj: TowerObject):
        return obj.group_id()

    def groups(self) -> set[tuple[int, 'Selection']]:
        data = sorted(filter(lambda obj: obj.group_id() >= 0, self), key=Selection._group_key)
        return {(group_id, Selection(group)) for group_id, group in itertools.groupby(data, Selection._group_key)}

    def ungrouped(self) -> 'Selection':
        return Selection({obj for obj in self if obj.group_id() < 0})

    def __hash__(self):
        return hash(tuple(self))


class Selector(ABC):
    def __init__(self, name):
        self.name = name

    # Selectors take in a Selection and output a new Selection.
    # Can think of these Selectors operating on the set of everything, and selecting a subset.
    # But nothing's stopping you from then selecting on that subset, and so on, further and further refining the
    #  selection using Selector objects.
    @abstractmethod
    def select(self, everything: Selection) -> Selection:
        pass


class NameSelector(Selector):
    def __init__(self, select_name):
        super().__init__('NameSelector')
        self.select_name = select_name.casefold()

    def select(self, everything: Selection) -> Selection:
        return Selection({obj for obj in everything if obj.matches_name(self.select_name)})


class CustomNameSelector(Selector):
    def __init__(self, select_name):
        super().__init__('CustomNameSelector')
        self.select_name = select_name.casefold()

    def select(self, everything: Selection) -> Selection:
        return Selection({obj for obj in everything if obj.get_custom_name().casefold() == self.select_name})


class ObjectNameSelector(Selector):
    def __init__(self, select_name):
        super().__init__('ObjectNameSelector')
        self.select_name = select_name.casefold()

    def select(self, everything: Selection) -> Selection:
        return Selection({obj for obj in everything if obj.get_name().casefold() == self.select_name})


class RegexSelector(Selector):
    def __init__(self, pattern):
        super().__init__('RegexSelector')
        self.pattern = re.compile(pattern)

    def select(self, everything: Selection) -> Selection:
        return Selection({obj for obj in everything if self.pattern.match(obj.get_name())
                          or self.pattern.match(obj.get_custom_name())})


class GroupSelector(Selector):
    def __init__(self, group_id):
        super().__init__('GroupSelector')
        self.group_id = group_id

    def select(self, everything: Selection) -> Selection:
        return Selection({obj for obj in everything if obj.group_id() == self.group_id})


class ItemSelector(Selector):
    def __init__(self):
        super().__init__('ItemSelector')

    def select(self, everything: Selection) -> Selection:
        return Selection({obj for obj in everything if obj.item is not None})


class EverythingSelector(Selector):
    def __init__(self):
        super().__init__('EverythingSelector')

    def select(self, everything: Selection) -> Selection:
        return everything

class NothingSelector(Selector):
    def __init__(self):
        super().__init__('NothingSelector')

    def select(self, everything: Selection) -> Selection:
        return Selection()
