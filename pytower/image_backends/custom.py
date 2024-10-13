from abc import ABC
from typing import IO

from .backend import ResourceBackend


class CustomBackend(ResourceBackend):
    """Custom backend stub for custom user implementations"""
    def __init__(self):
        """"""
        super().__init__('CustomCDN')

    # Must implement this!
    # upload_file: takes in file path and outputs url once uploaded
    def upload_file(self, path: str) -> str | None:
        raise NotImplementedError('Missing upload_image implementation!')
