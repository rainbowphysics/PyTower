import os.path
import sys

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from pytower.image_backends.backend import ResourceBackend
from pytower.logging import *


class CatboxBackend(ResourceBackend):
    def __init__(self, user_hash: str | None = None):
        super().__init__('Catbox')
        self.user_hash = user_hash

    def upload_file(self, path: str) -> str | None:
        url = 'https://catbox.moe/user/api.php'

        with open(path, 'rb') as file:

            # Optional: Add any additional form data required by the website
            filename = os.path.basename(path)
            ext = filename.split('.')[-1]
            data = {'reqtype': 'fileupload',
                    'fileToUpload': (path, file, f'image/{ext}')}  # Add any form data needed by the website

            if self.user_hash is not None:
                data['userhash'] = self.user_hash

            mp_encoder = MultipartEncoder(fields=data)

            # Send a POST request to the URL with the files and optional data
            headers = {
                'User-Agent': 'PyTower',
                'Content-Type': mp_encoder.content_type
            }
            response = requests.post(url, data=mp_encoder, headers=headers)

        if response.status_code == 200:
            # Successful upload
            return response.text
        else:
            # Upload failed
            error(f"Catbox upload failed with status code: {response.status_code}")
            return None
