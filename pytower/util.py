from __future__ import annotations

from dataclasses import dataclass
import io
import os
from collections import deque
from functools import reduce
from typing import Any, Callable, Literal, Mapping, Optional, Self, Sequence, TypeVar, cast, overload

import numpy as np
from numpy.typing import NDArray

from .uclasses.properties import TUPrimitive, TUStruct

T = TypeVar('T')

# Iteratively walks through dictionary using breadth-first search
def dict_walk(data: Mapping[str, Any] | None, func: Callable[[list[Any] | dict[str, Any] | Any], Any]):
    if data is None:
        return

    q = deque[Mapping[str, Any] | list[Any] | tuple[str, Any] | Any]([data])
    while len(q) > 0:
        elem = q.popleft()
        func(elem)
        if isinstance(elem, list) or isinstance(elem, tuple):
            for item in elem:
                q.append(item)
        elif isinstance(elem, dict):
            for k, v in elem.items():
                q.append((k, v))


def read_bytearray(fd: io.BytesIO, buf_size: int) -> bytearray:
    buf = bytearray(os.path.getsize(buf_size))
    fd.readinto(buf)
    return buf


def run_if_not_none(func: Callable[[T], Any], data: T | None):
    if data is not None:
        func(data)

XYZ_ARG = float | int | np.floating[Any] | np.signedinteger[Any]
XYZ_INT_ARG = int | np.signedinteger[Any]

class XYZ(NDArray[np.float64 | np.int32], TUStruct):
    StructName = 'Vector'
    IsBuiltIn = True

    @overload
    def __new__(cls, *xyz_int: *tuple[XYZInt]) -> XYZInt: ...
    #@overload
    #def __new__(*xyz_int: tuple[XYZ_INT_ARG, XYZ_INT_ARG, XYZ_INT_ARG]) -> XYZInt: ...
    @overload
    def __new__(cls, *xyz_int: *tuple[NDArray[np.signedinteger[Any]]]) -> XYZInt: ...

    @overload
    def __new__(cls, *xyz: *tuple[XYZ]) -> XYZ: ...
    @overload
    def __new__(cls, *xyz: *tuple[XYZ_ARG, XYZ_ARG, XYZ_ARG]) -> XYZ: ...
    @overload
    def __new__(cls, *xyz: *tuple[NDArray[np.floating[Any] | np.signedinteger[Any]]]) -> XYZ: ...
    @overload
    def __new__(cls, *xyz: *tuple[str]) -> XYZ: ...

    def __new__(cls, *args: XYZ | NDArray[Any] | str | XYZ_ARG) -> XYZ:
        new_instance = cast(XYZ, xyz(*args)).view(cls) # type: ignore

        if isinstance(new_instance[0], np.signedinteger):
            new_instance = cast(XYZInt, xyzint(new_instance)) # type: ignore

        return new_instance

    # TODO these static types are all wrong

    @classmethod
    def min(cls, *args: Self) -> Self: # type: ignore
        return cls(np.minimum(*args)) # type: ignore

    @classmethod
    def max(cls, *args: Self) -> Self: # type: ignore
        return cls(np.maximum(*args)) # type: ignore

    @property
    def x(self) -> float:
        return self[0]

    @x.setter
    def x(self, new: XYZ_ARG):
        self[0] = new

    @property
    def y(self) -> float:
        return self[1]

    @y.setter
    def y(self, new: XYZ_ARG):
        self[1] = new

    @property
    def z(self) -> float:
        return self[2]

    @z.setter
    def z(self, new: XYZ_ARG):
        self[2] = new

    def clamp(self, min_clamp: Self, max_clamp: Self) -> Self:
        return self.__class__.max(self.__class__.min(self, max_clamp), min_clamp)

    def distance(self, other: Self) -> np.floating[Any]:
        return np.linalg.norm(self - other)

    def norm(self) -> np.floating[Any]:
        return np.linalg.norm(self)

    def normalize(self):
        return self.__class__(*(self / self.norm()))

    def __eq__(self, other: Any): # type: ignore
        return np.isclose(self, other)

    @classmethod
    def from_dict(cls, dict: dict[str, Any]) -> Self:
        return cls(**dict)

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z
        }


class XYZInt(XYZ):
    pass


class XYZW(XYZ):
    StructName = 'Quat'
    IsBuiltIn = True

    @overload
    def __new__(cls, *xyzw: *tuple[XYZW]) -> XYZW: ...
    @overload
    def __new__(cls, *xyzw: *tuple[XYZ_ARG, XYZ_ARG, XYZ_ARG, XYZ_ARG]) -> XYZW: ...
    @overload
    def __new__(cls, *xyzw: *tuple[NDArray[np.floating[Any] | np.signedinteger[Any]]]) -> XYZW: ...
    @overload
    def __new__(cls, *xyzw: *tuple[str]) -> XYZW: ...

    def __new__(cls, *args: XYZW | XYZ_ARG | NDArray[Any] | str) -> 'XYZW':
        return cast(XYZW, xyz(*args, length=4)).view(cls) # type: ignore

    @property
    def w(self) -> float:
        return self[3]

    @w.setter
    def w(self, new: np.float64 | np.int32 | int | float):
        self[3] = new

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'w': self.w
        }

@overload
def xyz(*xyz_int: *tuple[XYZInt], length: Literal[3]=3) -> XYZInt: ...
#@overload
#def xyz(*xyz_int: tuple[XYZ_INT_ARG, XYZ_INT_ARG, XYZ_INT_ARG], length: Literal[3]=3) -> XYZInt: ...
@overload
def xyz(*xyz_int: *tuple[NDArray[np.signedinteger[Any]]], length: Literal[3]) -> XYZInt: ...

@overload
def xyz(*xyzw: *tuple[XYZW], length: Literal[4]=4) -> XYZW: ...
@overload
def xyz(*xyzw: *tuple[XYZ_ARG, XYZ_ARG, XYZ_ARG, XYZ_ARG], length: Literal[4]=4) -> XYZW: ...
@overload
def xyz(*xyzw: *tuple[NDArray[np.floating[Any] | np.signedinteger[Any]]], length: Literal[4]) -> XYZW: ...
@overload
def xyz(*xyzw: *tuple[str], length: Literal[4]) -> XYZW: ...

@overload
def xyz(*xyz: *tuple[XYZ], length: Literal[3]=3) -> XYZ: ...
@overload
def xyz(*xyz: *tuple[XYZ_ARG, XYZ_ARG, XYZ_ARG], length: Literal[3]=3) -> XYZ: ...
@overload
def xyz(*xyz: *tuple[NDArray[np.floating[Any] | np.signedinteger[Any]]], length: Literal[3]) -> XYZ: ...
@overload
def xyz(*xyz: *tuple[str], length: Literal[3]) -> XYZ: ...

def xyz(
    *args: XYZ | NDArray[Any] | str | XYZ_ARG,
    length: int=3
) -> XYZ | XYZW | XYZInt:
    if len(args) == 1:
        data = args[0]
        # Return argument if already is xyz
        if isinstance(data, XYZ):
            return data

        if isinstance(data, np.ndarray):
            if len(data) == 3:
                if isinstance(data[0], np.signedinteger):
                    return data.view(XYZInt)
                else:
                    return data.view(XYZ)
            elif len(data) == 4:
                return data.view(XYZW)

    # Constructor 1: x,y,z triplet
    if len(args) == length:
        nums = args
        for var in nums:
            if not isinstance(var, (float, np.floating, np.signedinteger, int)):
                raise ValueError(f'xyz expected float or int but got {type(var)}: {args}')

    # Constructor 2: 'x,y,z' string
    elif len(args) == 1:
        str_input = args[0]
        if not isinstance(str_input, str):
            raise ValueError(f'xyz expected str but got {type(str_input)}: {str_input}')

        nums = [float(e) for e in cast(str, args[0]).strip().split(',')]
    else:
        raise ValueError(f'xyz unexpected input: {args}. Did you pass the correct number of values?')

    if len(nums) != length:
        raise ValueError(f'xyz expected {length} values, not {len(nums)}: {args} is invalid')

    return np.array(nums).view(XYZ if length == 3 else XYZW)


@overload
def xyzint(*xyz: tuple[XYZ]) -> XYZInt: ...
@overload
def xyzint(*xyz: tuple[XYZ_ARG, XYZ_ARG, XYZ_ARG]) -> XYZInt: ...
@overload
def xyzint(*xyz: tuple[NDArray[np.floating[Any] | np.signedinteger[Any]]]) -> XYZInt: ...
@overload
def xyzint(*xyz: tuple[str]) -> XYZInt: ...

def xyzint(*args: tuple[XYZ | NDArray[Any] | str] | tuple[XYZ_ARG, XYZ_ARG, XYZ_ARG]) -> XYZInt:
    return np.rint(cast(XYZ, xyz(*args))).view(XYZInt) # type: ignore

_ScalarType_co = TypeVar("_ScalarType_co", bound=np.generic, covariant=True)
def xyz_to_string(data: NDArray[_ScalarType_co]):
    return f'{data[0]},{data[1]},{data[2]}'

if __name__ == '__main__':
    foo = XYZW(1.0, 2, 3, 4)
    foo.w = 10
    print(repr(foo))
    bar = XYZInt(1, 2, 3)
    print(repr(bar))

    print(repr(XYZ(*np.array([1,2,3.0]))))

# https://stackoverflow.com/a/71260806
def not_none(obj: Optional[T]) -> T:
    assert obj is not None
    return obj
