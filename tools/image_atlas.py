import hashlib
import os

import requests
import asyncio

from suitebro import Suitebro, TowerObject
from util import dict_walk

TOOL_NAME = 'ImageAtlas'


def hash_image(data: bytes):
    return hashlib.sha1(data, usedforsecurity=False).hexdigest()[:10]


async def download_image(url, img_dir):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            file_hash = hash_image(response.content)

            # Write the content to a file, using the hash to ensure uniqueness
            with open(os.path.join(img_dir, str(file_hash)), 'wb') as f:
                f.write(response.content)
            print(f'{url} downloaded successfully.')
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


async def download_images(urls, img_dir):
    return await asyncio.gather((download_image(url, img_dir) for url in urls))


def main(suitebro: Suitebro, selection: list[TowerObject], args):
    urls = set()

    def url_processor(dict_entry):
        if len(dict_entry) == 2:
            k, v = dict_entry
            if k == 'URL':
                urls.add(v['StrProperty'])

    for obj in suitebro.objects:
        dict_walk(obj.item, url_processor)

    # TODO add dating to this, so that each atlas is a true back-up
    # Also means you don't have to worry about file conflicts ;P
    image_dir = 'images'
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    results = asyncio.run(download_images())
