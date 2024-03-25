import io
import os
from typing import Any, Callable
from collections import deque


def dict_walk(data: dict, func: Callable[[list | dict | Any], Any]):
    q = deque([data])
    while len(q) > 0:
        elem = q.popleft()
        func(elem)
        if isinstance(elem, list):
            for item in elem:
                q.append(item)
        elif isinstance(elem, dict):
            for k, v in elem.items():
                q.append(k, v)


def read_bytearray(fd: io.BytesIO, buf_size: int) -> bytearray:
    buf = bytearray(os.path.getsize(buf_size))
    fd.readinto(buf)
    return buf
