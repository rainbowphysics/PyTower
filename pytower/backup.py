import hashlib
import json
import os
import struct
import sys
import datetime

import requests
import asyncio
from threading import Lock

from . import root_directory
from .config import KEY_INSTALL_PATH
from .suitebro import Suitebro
from .util import dict_walk

PRINT_LOCK = Lock()
BACKUP_DIR = os.path.join(root_directory, 'backup')


def _hash_image(data: bytes):
    return hashlib.sha1(data, usedforsecurity=False).hexdigest()[:10]


def print_safe(msg: str):
    with PRINT_LOCK:
        print(msg)


def _url_hash(url: str):
    return hashlib.md5(url.encode('ascii'), usedforsecurity=False).hexdigest()


def _read_cacheline(cache_path):
    buf = bytearray(os.path.getsize(cache_path))
    with open(cache_path, 'rb') as fd:
        fd.readinto(buf)

    # Based on https://github.com/brecert/tower-unite-cache/blob/main/hexpats/cache.hexpat
    data_size, = struct.unpack('<I', buf[:4])
    url_size, = struct.unpack('<I', buf[4:8])
    _url = buf[8:(8 + url_size)].decode('ascii')
    data = buf[(8 + url_size):(8 + url_size + data_size)]
    return data


def _write_image(url, data) -> str:
    file_hash = _hash_image(data)

    # Write the content to a file, using the hash to ensure uniqueness
    file_type = url.split('.')[-1]
    filename = f'{file_hash}.{file_type}'
    with open(filename, 'wb') as f:
        f.write(data)

    return filename


def _download_image(url, cache):
    # First check to see if url is in cache
    urlhash = _url_hash(url)
    if urlhash in cache:
        file_data = _read_cacheline(cache[urlhash])
        filename = _write_image(url, file_data)
        print_safe(f'Successfully retrieved {url} from the cache!')
        return url, filename

    try:
        # Send a GET request to the URL
        if not url.startswith('https://') and not url.startswith('http://'):
            url = 'http://' + url
        response = requests.get(url, headers={'User-agent': 'PyTower'})

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            filename = _write_image(url, response.content)

            print_safe(f'{url} downloaded successfully.')

            return url, filename
        else:
            print_safe(f"Failed to download {url}. Status code: {response.status_code}")
    except Exception as e:
        print_safe(f"An error occurred: {e}")

    return url, None


async def _download_images(urls, install_dir):
    # Try to locate canvas cache
    cache_path = os.path.join(os.path.join(os.path.join(install_dir, 'Tower'), 'Cache'), 'Canvas')
    canvas_cache = {}
    if os.path.isdir(cache_path):
        subdirs = [os.path.join(cache_path, subdir) for subdir in os.listdir(cache_path)]
        subdirs = [d for d in subdirs if os.path.isdir(d)]
        for subdir in subdirs:
            cachelines = [os.path.join(subdir, f) for f in os.listdir(subdir)]
            cachelines = [f for f in cachelines if os.path.isfile(f)]
            for cacheline in cachelines:
                md5_hash = os.path.basename(cacheline)[:-6]
                canvas_cache[md5_hash] = cacheline

    results = await asyncio.gather(*[asyncio.to_thread(_download_image, url, canvas_cache) for url in urls])

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


def make_backup(save: Suitebro):
    # First make the folder for the backup
    save_name = save.filename

    # If save is just default "CondoData", use parent folder for name
    if save_name == 'CondoData':
        save_name = os.path.basename(save.directory)

    # Sanitize save_name a little more
    save_name = save_name.replace(' ', '-').strip()

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
                urls.add(v['Str'])

    for obj in save.objects:
        dict_walk(obj.item, url_processor)
        dict_walk(obj.properties, url_processor)

    # Process URLs further
    urls = {url.strip() for url in urls if url.strip() != ''}

    # Now that all the URLs have been added to urls set, download them all
    from .config import CONFIG
    install_dir = CONFIG.get(KEY_INSTALL_PATH)
    asyncio.run(_download_images(urls, install_dir))

    # Return to previous cwd
    os.chdir(old_cwd)


def restore_backup(path):
    index_path = os.path.join(path, 'index.json')
    with open(index_path, 'r') as fd:
        index = json.load(fd)

    
