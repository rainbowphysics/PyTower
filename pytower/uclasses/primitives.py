from dataclasses import dataclass
from typing import Annotated, ClassVar
from .properties import IntProperty, SerializedName, StructProperty, TUPrimitive, TUStruct
from ..util import XYZ, XYZW

@dataclass(slots=True, frozen=True)
class Guid(TUPrimitive):
    a: int
    b: int
    c: int
    d: int

    StructName = 'Guid'
    IsBuiltIn = True

@dataclass(slots=True, frozen=True)
class Rotator(TUPrimitive):
    pitch: int
    yaw: int
    roll: int

    StructName = 'Rotator'
    IsBuiltIn = True

@dataclass(slots=True, frozen=True)
class Plane(TUPrimitive):
    w: float

    StructName = 'Plane'
    IsBuiltIn = True

@dataclass(slots=True, frozen=True)
class Vector2D(TUPrimitive):
    x: float
    y: float

    zero: ClassVar['Vector2D']
    one: ClassVar['Vector2D']

    StructName = 'Vector2D'
    IsBuiltIn = True

Vector2D.zero = Vector2D(0,0)
Vector2D.one = Vector2D(1,1)

@dataclass(slots=True, frozen=True)
class LinearColor(TUPrimitive):
    r: float
    g: float
    b: float
    a: float

    StructName = 'LinearColor'
    IsBuiltIn = True

@dataclass(slots=True, frozen=True)
class Color(TUPrimitive):
    r: int
    g: int
    b: int
    a: int

    StructName = 'Color'
    IsBuiltIn = True

class Colorable(TUStruct):
    StructName = __name__

    color: Annotated[LinearColor, StructProperty(LinearColor), SerializedName('Color')]
    dynamic_material_index: Annotated[int, IntProperty, SerializedName('DynamicMaterialIndex')]

class Transform(TUStruct):
    StructName = __name__

    rotation: Annotated[XYZW, StructProperty(XYZW), SerializedName('Rotation')]
    translation: Annotated[XYZ, StructProperty(XYZ), SerializedName('Translation')]
    scale_3d: Annotated[XYZ, StructProperty(XYZ), SerializedName('Scale3D')]