import io
import os
from collections import deque
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


def xyz(*args):
    # Return argument if already is xyz
    if len(args) == 1 and isinstance(args[0], np.ndarray):
        return args[0]

    # Constructor 1: x,y,z triplet
    if len(args) == 3:
        x, y, z = args
        for var in [x, y, z]:
            if (not isinstance(var, float) and not isinstance(var, int) and not isinstance(var, np.int32)
                    and not isinstance(var, np.float32)):
                raise ValueError(f'xyz expected float or int but got {type(var)}: {args}')

    # Constructor 2: 'x,y,z' string
    elif len(args) == 1:
        str_input = args[0]
        if not isinstance(str_input, str):
            raise ValueError(f'xyz expected str but got {type(str_input)}: {str_input}')

        x, y, z = [float(e) for e in args[0].strip().split(',')]
    else:
        raise ValueError(f'xyz unexpected input: {args}')

    return np.array([x, y, z])


def xyzint(*args):
    return np.int_(xyz(*args) + .5)


def xyz_to_string(data: np.ndarray):
    return f'{data[0]},{data[1]},{data[2]}'


def xyz_max(x1: np.ndarray, x2: np.ndarray):
    return np.maximum(x1, x2)


def xyz_min(x1: np.ndarray, x2: np.ndarray):
    return np.minimum(x1, x2)


def xyz_clamp(x: np.ndarray, min_clamp: np.ndarray, max_clamp: np.ndarray):
    return xyz_max(xyz_min(x, max_clamp), min_clamp)


def xyz_equal(x: np.ndarray, y: np.ndarray):
    return np.isclose(x, y)


def xyz_distance(x: np.ndarray, y: np.ndarray):
    return np.linalg.norm(x - y)
