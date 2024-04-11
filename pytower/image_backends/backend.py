import asyncio
import sys
import threading
from abc import ABC, abstractmethod
from typing import Iterable, IO


class ResourceBackend(ABC):
    def __init__(self, name):
        self.name = name
        self.print_lock = threading.Lock()

    def safe_print(self, *args, **kwargs):
        with self.print_lock:
            print(*args, **kwargs)

    # Upload image takes as input a path and returns the uploaded url
    @abstractmethod
    def upload_file(self, path: str) -> str | None:
        pass

    def _upload_thread(self, path: str) -> str | None:
        try:
            url = self.upload_file(path)
            if url:
                self.safe_print(f'Successfully uploaded {path} to {self.name}: {url}')

            return url
        except Exception as e:
            self.safe_print(f'Error while uploading file: {e}', file=sys.stderr)
            return None

    async def _upload_async(self, files: Iterable[str]) -> dict:
        results = await asyncio.gather(*[asyncio.to_thread(self._upload_thread, path) for path in files])
        # Zip each file with its result
        zipped = zip(files, results)
        # Filter out Nones
        zipped = [zresult for zresult in zipped if zresult[1]]
        # Convert to dict with dict comprehension
        return {k: v for k, v in zipped}

    # Default implementation that can be overridden for performance and to avoid rate limiting
    # Return value is dict where paths are keys and urls are values
    def upload_files(self, files: Iterable[str]) -> dict:
        return asyncio.run(self._upload_async(files))
