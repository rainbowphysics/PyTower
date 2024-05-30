from dataclasses import dataclass
from typing import Annotated, ClassVar
from .properties import IntProperty, SerializedName, StructProperty, TUPrimitive, TUStruct
from ..util import XYZ, XYZW

# TODO: Find a better way to do this, because XYZ is a numpy array and we can't detect mutations to it...
@dataclass(slots=True, frozen=True)
class Vector(TUPrimitive):
    x: float
    y: float
    z: float

    zero: ClassVar['Vector']
    one: ClassVar['Vector']

    StructName = 'Vector'
    IsBuiltIn = True

    def to_xyz(self) -> XYZ:
        return XYZ(self.x, self.y, self.z)

    @staticmethod
    def from_xyz(xyz: XYZ):
        return Vector(xyz.x, xyz.y, xyz.z)

Vector.zero = Vector(0,0,0)
Vector.one = Vector(1,1,1)

@dataclass(slots=True, frozen=True)
class Quat(TUPrimitive):
    x: float
    y: float
    z: float
    w: float

    zero: ClassVar['Quat']
    one: ClassVar['Quat']

    StructName = 'Quat'
    IsBuiltIn = True

    def to_xyzw(self) -> XYZW:
        return XYZW(self.x, self.y, self.z, self.w)

    @staticmethod
    def from_xyzw(xyzw: XYZW):
        return Quat(xyzw.x, xyzw.y, xyzw.z, xyzw.w)

Quat.zero = Quat(0,0,0,0)
Quat.one = Quat(1,1,1,1)

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

    rotation: Annotated[Quat, StructProperty(Quat), SerializedName('Rotation')]
    translation: Annotated[Vector, StructProperty(Vector), SerializedName('Translation')]
    scale_3d: Annotated[Vector, StructProperty(Vector), SerializedName('Scale3D')]