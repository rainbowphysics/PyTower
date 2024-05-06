import io
import os
from collections import deque
from functools import reduce
from typing import Any, Callable

import numpy as np


# Iteratively walks through dictionary using breadth-first search
def dict_walk(data: dict, func: Callable[[list | dict | Any], Any]):
    if data is None:
        return

    q = deque([data])
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


def run_if_not_none(func, data):
    if data is not None:
        func(data)


class XYZ(np.ndarray):
    def __new__(cls, *args) -> 'XYZ':
        new_instance = xyz(*args).view(cls)

        if isinstance(new_instance[0], np.int32):
            new_instance = xyzint(new_instance)

        return new_instance

    @staticmethod
    def fold(func: Callable[['XYZ', 'XYZ'], 'XYZ'], *args: 'XYZ', acc=None):
        if acc is None:
            acc = args[0]
            args = args[1:]
        return reduce(lambda a, b: func(a, b), args, acc)

    @staticmethod
    def min(*args: 'XYZ'):
        return XYZ.fold(np.minimum, *args)

    @staticmethod
    def max(*args: 'XYZ'):
        return XYZ.fold(np.maximum, *args)

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, new):
        self[0] = new

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, new):
        self[1] = new

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, new):
        self[2] = new

    def clamp(self, min_clamp: 'XYZ', max_clamp: 'XYZ'):
        return XYZ.max(XYZ.min(self, max_clamp), min_clamp)

    def distance(self, other: 'XYZ'):
        return np.linalg.norm(self - other)

    def norm(self):
        return np.linalg.norm(self)

    def normalize(self):
        return self / self.norm()

    def __eq__(self, other: 'XYZ'):
        return np.isclose(self, other)


class XYZInt(XYZ):
    pass


class XYZW(XYZ):
    def __new__(cls, *args) -> 'XYZW':
        return xyz(*args, length=4).view(cls)

    @property
    def w(self):
        return self[3]

    @w.setter
    def w(self, new):
        self[3] = new


def xyz(*args, length=3) -> XYZ:
    # Return argument if already is xyz
    if len(args) == 1 and isinstance(args[0], np.ndarray):
        return args[0]

    # Constructor 1: x,y,z triplet
    if len(args) == length:
        nums = args
        for var in nums:
            if (not isinstance(var, float) and not isinstance(var, int) and not isinstance(var, np.int32)
                    and not isinstance(var, np.float32)):
                raise ValueError(f'xyz expected float or int but got {type(var)}: {args}')

    # Constructor 2: 'x,y,z' string
    elif len(args) == 1:
        str_input = args[0]
        if not isinstance(str_input, str):
            raise ValueError(f'xyz expected str but got {type(str_input)}: {str_input}')

        nums = [float(e) for e in args[0].strip().split(',')]
    else:
        raise ValueError(f'xyz unexpected input: {args}. Did you pass the correct number of values?')

    if len(nums) != length:
        raise ValueError(f'xyz expected {length} values, not {len(nums)}: {args} is invalid')

    return np.array(nums).view(XYZ)


def xyzint(*args):
    return np.int_(xyz(*args) + .5).view(XYZInt)


def xyz_to_string(data: np.ndarray):
    return f'{data[0]},{data[1]},{data[2]}'


if __name__ == '__main__':
    foo = XYZW(1.0, 2, 3, 4)
    foo.w = 10
    print(repr(foo))
    bar = XYZInt(1, 2, 3)
    print(repr(bar))
