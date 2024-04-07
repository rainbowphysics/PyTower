import hashlib
import json
import os
import sys
import datetime

import requests
import asyncio
from threading import Lock

import pytower
from pytower.suitebro import Suitebro
from pytower.util import dict_walk

PRINT_LOCK = Lock()
BACKUP_DIR = os.path.join(pytower.root_directory, 'backup')


def hash_image(data: bytes):
    return hashlib.sha1(data, usedforsecurity=False).hexdigest()[:10]


def print_safe(msg: str):
    with PRINT_LOCK:
        print(msg)

def _download_image(url):
    try:
        # Send a GET request to the URL
        if not url.startswith('https://') and not url.startswith('http://'):
            url = 'http://' + url
        response = requests.get(url, headers={'User-agent': 'PyTower'})

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            file_hash = hash_image(response.content)

            # Write the content to a file, using the hash to ensure uniqueness
            file_type = url.split('.')[-1]
            filename = f'{file_hash}.{file_type}'
            with open(filename, 'wb') as f:
                f.write(response.content)

            print_safe(f'{url} downloaded successfully.')

            return url, filename
        else:
            print_safe(f"Failed to download {url}. Status code: {response.status_code}")
    except Exception as e:
        print_safe(f"An error occurred: {e}")

    return url, None


async def _download_images(urls):
    results = await asyncio.gather(*[asyncio.to_thread(_download_image, url) for url in urls])

    # Create backup index
    index = {}
    for url, filename in results:
        if filename is not None:
            index[url] = filename

    with open('index.json', 'w') as fd:
        json.dump(index, fd, indent=2)

    # Now create replacement index
    replacements = {}
    for url, filename in results:
        if filename is not None:
            replacements[url] = None

    with open('replacement_index.json', 'w') as fd:
        json.dump(replacements, fd, indent=2)


def save_resources(save: Suitebro):
    # First make the folder for the backup
    save_name = save.filename

    # If save is just default "CondoData", use parent folder for name
    if save_name == 'CondoData':
        save_name = save.directory

    cur_time = datetime.datetime.now()
    timestamp = str(cur_time).replace(' ', '-').replace(':', '-')

    backup_path = os.path.join(BACKUP_DIR, f'{save_name}_{timestamp}')
    os.makedirs(backup_path)

    # chdir to it
    old_cwd = os.getcwd()
    os.chdir(backup_path)

    # Gather all URLs
    urls = set()

    def url_processor(dict_entry):
        if isinstance(dict_entry, tuple) and len(dict_entry) == 2:
            k, v = dict_entry
            if k == 'URL' or k == 'CanvasURL':
                urls.add(v['StrProperty'])

    for obj in save.objects:
        dict_walk(obj.item, url_processor)
        dict_walk(obj.properties, url_processor)

    # Process URLs further
    urls = {url.strip() for url in urls if url.strip() != ''}

    # Now that all the URLs have been added to urls set, download them all
    asyncio.run(_download_images(urls))

    # Return to previous cwd
    os.chdir(old_cwd)
