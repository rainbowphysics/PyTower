from typing import Iterable

import requests

from .backend import ResourceBackend
from ..logging import *

IMGUR_API = "https://api.imgur.com/3/upload"


class ImgurBackend(ResourceBackend):
    """Imgur backend that based on submitting POST requests to https://api.imgur.com/3/upload"""
    def __init__(self, client_id):
        """

        Args:
            client_id: Imgur client ID to use
        """
        super().__init__('Imgur')
        self.client_id = client_id

    def upload_file(self, path: str) -> str | None:

        headers = {'Authorization': f'Client-ID {self.client_id}'}

        # Open the image file
        with open(path, 'rb') as f:
            # Send POST request to Imgur API
            response = requests.post(IMGUR_API, headers=headers, files={'image': f})

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # The direct link to the uploaded image
            return data['data']['link']
        else:
            # Request was not successful
            error(f"Error uploading image: {response.status_code} {response.reason}")
            return None

    def upload_files(self, files: Iterable[str]) -> dict[str, str]:
        return super().upload_files(files)
