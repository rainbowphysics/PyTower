import copy
import itertools
import random

from .object import TowerObject

from abc import ABC, abstractmethod
import re

from .util import XYZ


class Selection(set[TowerObject]):
    @staticmethod
    def _group_key(obj: TowerObject):
        return obj.group_id

    @property
    def group_id(self) -> int:
        return self.groups().pop()[0]

    @group_id.setter
    def group_id(self, value: int):
        for obj in self:
            obj.group_id = value

    @group_id.deleter
    def group_id(self):
        self.destroy_groups()

    def group(self) -> int:
        """Creates a new group based on the selection

        Returns:
            Group ID of the new group
        """
        from .suitebro import get_active_save
        return get_active_save().group(self)

    def groups(self) -> set[tuple[int, 'Selection']]:
        """
        Returns:
            Groups present in the Selection, as a set of tuples in the form (group_id: int, sel: Selection)
        """
        data = sorted(filter(lambda obj: obj.group_id >= 0, self), key=Selection._group_key)
        return {(group_id, Selection(group)) for group_id, group in itertools.groupby(data, Selection._group_key)}

    def ungrouped(self) -> 'Selection':
        """
        Returns:
            TowerObjects in the Selection without a group_id
        """
        return Selection({obj for obj in self if obj.group_id < 0})

    def destroy_groups(self):
        """Destroys all groups in the selection, rendering the objects ungrouped."""
        for obj in self:
            obj.ungroup()

    def get(self) -> TowerObject | None:
        """
        Converts Selection into TowerObject, which is useful when only one TowerObject is expected

        Returns:
            Gets the first object in this Selection object, or None if Selection is empty

        """
        return next(iter(self)) if len(self) != 0 else None

    def __add__(self, other: 'Selection') -> 'Selection':
        """Implements the + operator as union for Selection objects"""
        if not isinstance(other, Selection):
            raise ValueError(f'Cannot add Selection with {type(other)}!')

        return Selection(self.union(other))

    def __iadd__(self, other: 'Selection') -> 'Selection':
        """Implements the += operator as union for Selection objects"""
        if not isinstance(other, Selection):
            raise ValueError(f'Cannot add Selection with {type(other)}!')

        self.update(other)
        return self

    def __sub__(self, other: 'Selection') -> 'Selection':
        """Implements the - operator as set difference for Selection objects"""
        if not isinstance(other, Selection):
            raise ValueError(f'Cannot add Selection with {type(other)}!')

        return Selection(self.difference(other))

    def __isub__(self, other: 'Selection') -> None:
        """Implements the -= operator as set difference for Selection objects"""
        if not isinstance(other, Selection):
            raise ValueError(f'Cannot add Selection with {type(other)}!')

        self.difference_update(other)
        return self

    def __mul__(self, other: 'Selection') -> 'Selection':
        """Implements the \\* operator as intersection for Selection objects"""
        if not isinstance(other, Selection):
            raise ValueError(f'Cannot multiply Selection with {type(other)}!')

        return Selection(self.intersection(other))

    def __imul__(self, other: 'Selection') -> None:
        """Implements the \\*= operator as intersection for Selection objects"""
        if not isinstance(other, Selection):
            raise ValueError(f'Cannot multiply Selection with {type(other)}!')

        self.intersection_update(other)
        return self

    def __hash__(self):  # type: ignore # set overrides __hash__=None, we override it again
        return hash(tuple(self))


class Selector(ABC):
    def __init__(self, name):
        """
        Args:
            name: Printed name for Selector object
        """
        self.name = name

    @abstractmethod
    def select(self, everything: Selection) -> Selection:
        """
        Selectors take in a Selection and output a new Selection. You can think of these Selectors operating on the
        set of everything, and selecting a subset. However, nothing's stopping you from then selecting on that subset,
        and so on, further and further refining the selection using Selector objects.

        Args:
            everything: Everything the Selector selects on

        Returns:
            A new refined Selection object
        """
        pass

    def __repr__(self):
        self_vars = copy.copy(vars(self))
        del self_vars['name']
        return f'{self.name}[{self_vars}]'


class NameSelector(Selector):
    def __init__(self, select_name: str):
        super().__init__('NameSelector')
        self.select_name = select_name.casefold()

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection where each object's name or custom name matches self.select_name
        """
        return Selection({obj for obj in everything if obj.matches_name(self.select_name)})


class CustomNameSelector(Selector):
    def __init__(self, select_name: str):
        super().__init__('CustomNameSelector')
        self.select_name = select_name.casefold()

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection where each object's custom name matches self.select_name
        """
        return Selection({obj for obj in everything if obj.get_custom_name().casefold() == self.select_name})


class ObjectNameSelector(Selector):
    def __init__(self, select_name: str):
        super().__init__('ObjectNameSelector')
        self.select_name = select_name.casefold()

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection where each object's name matches self.select_name
        """
        return Selection({obj for obj in everything if obj.get_name().casefold() == self.select_name})


class RegexSelector(Selector):
    def __init__(self, pattern: str):
        super().__init__('RegexSelector')
        self.pattern = re.compile(pattern.casefold())

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection where each object's name or custom name matches the self.pattern regular expression pattern
        """
        return Selection({obj for obj in everything if self.pattern.match(obj.get_name().casefold())
                          or self.pattern.match(obj.get_custom_name().casefold())})


class GroupSelector(Selector):
    def __init__(self, group_id: int):
        super().__init__('GroupSelector')
        self.group_id = group_id

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection where each object's group id matches self.group_id
        """
        return Selection({obj for obj in everything if obj.group_id == self.group_id})


class ItemSelector(Selector):
    def __init__(self):
        super().__init__('ItemSelector')

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection excluding objects that only have a properties section
        """
        return Selection({obj for obj in everything if obj.item is not None})


class EverythingSelector(Selector):
    def __init__(self):
        super().__init__('EverythingSelector')

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            The input Selection, acting as an identity function
        """
        return everything


class NothingSelector(Selector):
    def __init__(self):
        super().__init__('NothingSelector')

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            An empty Selection. Potentially useful when a tool doesn't depend on input selection
        """
        return Selection()


class PercentSelector(Selector):
    def __init__(self, percentage: float):
        super().__init__('PercentSelector')
        self.percentage = percentage

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection with a random subset of self.percentage % of objects
        """
        sequence = list(everything)
        random.shuffle(sequence)
        cutoff = int(len(sequence) * self.percentage / 100 + 0.5)
        return Selection(sequence[0:cutoff])


class TakeSelector(Selector):
    def __init__(self, number: int):
        super().__init__('TakeSelector')
        self.number = number

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection with a random subset of self.number of objects
        """
        sequence = list(everything)
        random.shuffle(sequence)
        return Selection(sequence[0:self.number])


class RandomSelector(Selector):
    def __init__(self, probability: float):
        super().__init__('RandomSelector')
        self.probability = probability

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection where every object is selected with probability self.probability
        """
        return Selection({obj for obj in everything if random.uniform(0, 1) <= self.probability})


class BoxSelector(Selector):
    def __init__(self, pos1: XYZ, pos2: XYZ):
        super().__init__('BoxSelector')
        self.min_pos = XYZ.min(pos1, pos2)
        self.max_pos = XYZ.max(pos1, pos2)

    def _contains(self, pos: XYZ):
        if pos is not None:
            return pos == pos.clamp(self.min_pos, self.max_pos)
        return False

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection of objects contained in the box formed by self.min_pos and self.max_pos
        """
        return Selection({obj for obj in everything if self._contains(obj.position)})


class SphereSelector(Selector):
    def __init__(self, center: XYZ, radius: float):
        super().__init__('SphereSelector')
        self.center = center
        self.radius = radius

    def _contains(self, pos: XYZ) -> bool:
        if pos is not None:
            return self.center.distance(pos) < self.radius
        return False

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection of objects contained in the sphere defined by self.center and self.radius
        """
        return Selection({obj for obj in everything if self._contains(obj.position)})


class UnionSelector(Selector):
    def __init__(self, left: Selector, right: Selector):
        super().__init__('UnionSelector')
        self.left = left
        self.right = right

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection union of self.left and self.right selectors applied to input
        """
        return self.left.select(everything) + self.right.select(everything)


class CompositionSelector(Selector):
    def __init__(self, left: Selector, right: Selector):
        super().__init__('CompositionSelector')
        self.left = left
        self.right = right

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection composition of self.left applied to Selection input, followed by self.right
        """
        return self.right.select(self.left.select(everything))


class IntersectionSelector(Selector):
    def __init__(self, left: Selector, right: Selector):
        super().__init__('IntersectionSelector')
        self.left = left
        self.right = right

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection composition of self.left applied to Selection input, followed by self.right
        """
        return self.left.select(everything) * self.right.select(everything)


class DifferenceSelector(Selector):
    def __init__(self, left: Selector, right: Selector):
        super().__init__('DifferenceSelector')
        self.left = left
        self.right = right

    def select(self, everything: Selection) -> Selection:
        """
        Returns:
            Selection composition of self.left applied to Selection input, followed by self.right
        """
        return self.left.select(everything) - self.right.select(everything)
