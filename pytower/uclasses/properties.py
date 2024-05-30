from __future__ import annotations
from abc import ABC
from inspect import isabstract, isclass
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Protocol, Self, TypeVar, Union, cast, dataclass_transform, get_args, get_type_hints, runtime_checkable, Annotated
from dataclasses import asdict, dataclass, fields

T = TypeVar('T')
TCo = TypeVar('TCo', covariant=True)

@dataclass(frozen=True, slots=True)
class UEnum:
    value: str

    @property
    def enum_type(self):
        return self.value[:self.value.index('::')]

    @property
    def enum_value(self):
        return self.value[(self.value.index('::') + 2):]

@dataclass(frozen=True, slots=True)
class Name:
    name: str

@dataclass(frozen=True, slots=True)
class Object:
    object: str
    property_class: str

    def create_from(self, object: str):
        return Object(object, self.property_class)

@runtime_checkable
class PropertyConverter(Protocol[T]): # Python 3.12: move [T] to after PropertyConverter
    def is_defined(self, value: Any) -> bool:
        """Checks whether the property is defined."""
        ...

    def get(self, value: Any) -> T:
        """Gets the property's value."""
        ...

    def set(self, serialized_value: Any, new_value: T) -> Any:
        """Sets the property's value."""
        ...

class BoolProperty(PropertyConverter[bool]):
    TypeName = 'Bool'

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) and __class__.TypeName in value and 'value' in value[__class__.TypeName]

    def get(self, value: Any) -> bool:
        return value[__class__.TypeName]['value']

    def set(self, serialized_value: Any, new_value: bool) -> Any:
        return { __class__.TypeName: { "value": new_value } }

class IntProperty(PropertyConverter[int]):
    TypeName = 'Int'

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) and __class__.TypeName in value and 'value' in value[__class__.TypeName]

    def get(self, value: Any) -> int:
        return value[__class__.TypeName]['value']

    def set(self, serialized_value: Any, new_value: int) -> Any:
        return { __class__.TypeName: { "value": new_value } }

class ByteProperty(PropertyConverter[int]):
    TypeName = 'Byte'

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) and __class__.TypeName in value and 'value' in value[__class__.TypeName]

    def get(self, value: Any) -> int:
        return value[__class__.TypeName]['value']

    def set(self, serialized_value: Any, new_value: int) -> Any:
        return { __class__.TypeName: { "value": new_value } }

class FloatProperty(PropertyConverter[float]):
    TypeName = 'Float'

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) and __class__.TypeName in value and 'value' in value[__class__.TypeName]

    def get(self, value: Any) -> float:
        return value[__class__.TypeName]['value']

    def set(self, serialized_value: Any, new_value: float) -> Any:
        return { __class__.TypeName: { "value": new_value } }

class StrProperty(PropertyConverter[str]):
    TypeName = 'Str'

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) and __class__.TypeName in value and 'value' in value[__class__.TypeName]

    def get(self, value: Any) -> str:
        return value[__class__.TypeName]['value']

    def set(self, serialized_value: Any, new_value: str) -> Any:
        return { __class__.TypeName: { "value": new_value } }

class TextProperty(PropertyConverter[str]):
    TypeName = 'Text'

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) and __class__.TypeName in value and 'value' in value[__class__.TypeName]

    def get(self, value: Any) -> str:
        return value[__class__.TypeName]['value']

    def set(self, serialized_value: Any, new_value: str) -> Any:
        return { __class__.TypeName: { "value": new_value } }

class EnumProperty(PropertyConverter[UEnum]):
    TypeName = 'Enum'

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) and __class__.TypeName in value and 'value' in value[__class__.TypeName]

    def get(self, value: Any) -> UEnum:
        return UEnum(value[__class__.TypeName]['value'])

    def set(self, serialized_value: Any, new_value: UEnum) -> Any:
        return { __class__.TypeName: { "value": new_value.value, "enum_type": new_value.enum_type } }

class NameProperty(PropertyConverter[Name]):
    TypeName = 'Name'

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) and __class__.TypeName in value and 'value' in value[__class__.TypeName]

    def get(self, value: Any) -> Name:
        return Name(value[__class__.TypeName]['value'])

    def set(self, serialized_value: Any, new_value: Name) -> Any:
        return { __class__.TypeName: { "value": new_value.name } }

class ObjectProperty(PropertyConverter[Object]):
    TypeName = 'Object'

    property_class: str

    def __init__(self, property_class: str):
        self.property_class = property_class

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) and __class__.TypeName in value and 'value' in value[__class__.TypeName]

    def get(self, value: Any) -> Object:
        return Object(value[__class__.TypeName]['value'], self.property_class)

    def set(self, serialized_value: Any, new_value: Object) -> Any:
        return { __class__.TypeName: { "value": new_value.object } }

class TUStruct(Protocol):
    StructName: ClassVar[str]
    IsBuiltIn: ClassVar[bool] = False

    @classmethod
    def from_dict(cls, dict: dict[str, Any]) -> Self:
        ...

    def to_dict(self) -> dict[str, Any]:
        ...

TStruct = TypeVar('TStruct', bound=TUStruct)
class StructProperty(PropertyConverter[TStruct]):
    type: type[TStruct]

    def __init__(self, type: type[TStruct]):
        self.type = type

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) \
            and 'Struct' in value \
            and 'value' in value['Struct'] \
            and (self.type.StructName if self.type.IsBuiltIn else 'Struct') in value['Struct']['value']

    def get(self, value: Any) -> TStruct:
        return self.type.from_dict(value['Struct']['value'][self.type.StructName if self.type.IsBuiltIn else 'Struct'])

    def set(self, serialized_value: Any, new_value: TStruct) -> Any:
        serialized_dict = cast(serialized_value, dict[str, Any])

        return {
            "Struct": {
                "value": {
                    self.type.StructName if self.type.IsBuiltIn else 'Struct': new_value.to_dict()
                },
                "struct_type": self.type.StructName if self.type.IsBuiltIn else {
                    "Struct": self.type.StructName
                },
                "struct_id": serialized_dict['Struct']['struct_id'] \
                    if isinstance(serialized_value, dict) \
                    and 'Struct' in serialized_dict \
                    and 'struct_id' in serialized_dict['Struct'] \
                    else "00000000-0000-0000-0000-000000000000"
            }
        }

class ArrayProperty(PropertyConverter[list[T]]):
    def __init__(self, array_of_property_name: str, inner_converter: PropertyConverter[T]):
        self.array_of_property_name = array_of_property_name
        self.inner_converter = inner_converter

    def is_defined(self, value: Any) -> bool:
        return isinstance(value, dict) \
            and 'Array' in value \
            and 'value' in value['Array'] # TODO

    def get(self, value: Any) -> list[T]:
        return None # type: ignore # TODO

    def set(self, serialized_value: Any, new_value: list[T]) -> dict[str, Any]:
        if not isinstance(self.inner_converter, StructProperty):
            raise Exception(f'Not implemented: ArrayProperty of {self.inner_converter.__class__}')

        serialized_dict = cast(serialized_value, dict[str, Any])
        propconv = cast(StructProperty[T], self.inner_converter) # type: ignore

        return {
          "Array": {
            "array_type": self.inner_converter.__class__.__name__, # TODO
            "value": { # inner_val
              "Struct": {
                "_type": self.array_of_property_name,
                "name": self.inner_converter.__class__.__name__, # TODO
                "struct_type": cast(TUStruct, propconv.type).StructName if cast(TUStruct, propconv.type).IsBuiltIn else {
                    "Struct": cast(TUStruct, propconv.type).StructName
                },
                "id": serialized_dict['Array']['value']['Struct']['id'] \
                    if isinstance(serialized_value, dict) \
                    and 'Array' in serialized_dict \
                    and 'value' in serialized_dict['Array'] \
                    and 'Struct' in serialized_dict['Array']['value'] \
                    and 'id' in serialized_dict['Array']['value']['Struct'] \
                    else "00000000-0000-0000-0000-000000000000",
                "value": None # TODO
              }
            }
          }
        }

@dataclass(frozen=True, slots=True)
class SerializedName:
    name: str

class SuitebroDataclass(TUStruct):
    props: dict[str, Any]

    def __init__(self, dict: dict[str, Any]):
        ...

#property_types: dict[type[Any], PropertyConverter[Any]] = {
#    bool: BoolProperty(),
#    str: StrProperty(),
#
#    int: IntProperty(),
#    float: FloatProperty(),
#    Name: NameProperty(),
#}

TDataclass = TypeVar('TDataclass', bound=SuitebroDataclass)
def suitebro_dataclass(cls: type[TDataclass]):
    @dataclass(frozen=True, slots=True)
    class FieldType:
        name: str
        serialized_name: str
        type: type[Any]
        converter: PropertyConverter[Any]

    def get_actual_type(k: str, type: Any) -> Optional[FieldType]:
        if isinstance(type, Annotated):
            serialized_name = k

            args = get_args(type)

            converter: PropertyConverter[Any] | None = None

            for t in args:
                if isinstance(t, PropertyConverter):
                    converter = t
                elif isinstance(t, SerializedName):
                    serialized_name = t.name
                elif isclass(t):
                    type = t
                else:
                    # brother what
                    raise SyntaxError(f'Bad prop syntax: invalid type {t}')

            if not converter:
                    raise SyntaxError('No converter')

            return FieldType(k, serialized_name, type, converter)

        return None

    # cls = dataclass(cls)

    for k, v in get_type_hints(cls, include_extras=True).items():
        f = get_actual_type(k, v)
        if f is None: continue

        p = f.converter
        sn = f.serialized_name
        # property_types[f.type].get(kwargs[f.serialized_name])

        def fget(self: SuitebroDataclass):
            if sn not in self.props: return None

            v = self.props[sn]
            if not p.is_defined(v): return None

            return p.get(v)

        def fset(self: SuitebroDataclass, value: Any):
            self.props[sn] = p.set(fget(self), value)

        setattr(cls, f.name, property(
            fget,
            fset
        ))

    return cls

class DataclassInstance(Protocol):
    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[dict[str, Any]]

class TUPrimitive(ABC, DataclassInstance, TUStruct):
    @classmethod
    def from_dict(cls, dict: dict[str, Any]) -> Self:
        return cls(**dict)

    def to_dict(self):
        if hasattr(self, "__dict__"):
            return self.__dict__
        return asdict(self)

class TUObjectPropertyCollection(SuitebroDataclass, TUStruct):
    props: dict[str, Any]

    StructName = None # type: ignore
    IsBuiltIn = False

    def __init__(self, dict: dict[str, Any]):
        self.props = dict

    def to_dict(self) -> dict[str, Any]:
        return self.props

    @classmethod
    def from_dict(cls, dict: dict[str, Any]) -> Self:
        return cls(dict)

# usage:
if __name__ == '__main__':
    from pytower.uclasses.classes import PhysicalMediaShelf_C

    shelf = PhysicalMediaShelf_C(dict={
        "SpacerMultiplier": {
            "Float": {
                "value": 69.420
            }
        }
    })
    shelf.spacer_multiplier = 420.69
    shelf.props # serialized!
