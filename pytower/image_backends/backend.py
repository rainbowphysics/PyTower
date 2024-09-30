import asyncio
import sys
import threading
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable, IO, Literal, ParamSpec, Protocol, TypeVar, cast
from pytower.logging import *


class ResourceBackend(ABC):
    def __init__(self, name: str):
        self.name = name

    # Upload image takes as input a path and returns the uploaded url
    @abstractmethod
    def upload_file(self, path: str) -> str | None:
        pass

    def _upload_thread(self, path: str) -> str | None:
        try:
            url = self.upload_file(path)
            if url:
                info(f'Successfully uploaded {path} to {self.name}: {url}')

            return url
        except Exception as e:
            error(f'Error while uploading file: {e}')
            return None

    async def _upload_async(self, files: Iterable[str]) -> dict[str, str]:
        results = await asyncio.gather(*[asyncio.to_thread(self._upload_thread, path) for path in files])
        # Zip each file with its result
        zipped = zip(files, results)
        # Filter out Nones
        zipped = cast(list[tuple[str, str]], [zresult for zresult in zipped if zresult[1]])
        # Convert to dict with dict comprehension
        return {k: v for k, v in zipped}

    # Default implementation that can be overridden for performance and to avoid rate limiting
    # Return value is dict where paths are keys and urls are values
    def upload_files(self, files: Iterable[str]) -> dict[str, str]:
        return asyncio.run(self._upload_async(files))
