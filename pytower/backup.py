import hashlib
import json
import logging
import os
import struct
import sys
import datetime
from typing import Any, Collection
from typing_extensions import Buffer

import requests
import asyncio
from colorama import Fore, Back, Style

from .__config__ import root_directory, __version__
from .config import KEY_INSTALL_PATH
from .image_backends.backend import ResourceBackend
from .image_backends.catbox import CatboxBackend
from .logging import *
from .suitebro import Suitebro, load_suitebro, save_suitebro
from .tool_lib import ParameterDict
from .util import dict_walk
from .selection import Selection
from .tools import replace_url

BACKUP_DIR = os.path.join(root_directory, 'backup')


def _hash_image(data: Buffer):
    return hashlib.sha1(data, usedforsecurity=False).hexdigest()[:10]


def _url_hash(url: str):
    return hashlib.md5(url.encode('ascii'), usedforsecurity=False).hexdigest()


def _read_cacheline(cache_path: str) -> bytearray:
    buf = bytearray(os.path.getsize(cache_path))
    with open(cache_path, 'rb') as fd:
        fd.readinto(buf)

    # Based on https://github.com/brecert/tower-unite-cache/blob/main/hexpats/cache.hexpat
    data_size, = struct.unpack('<I', buf[:4])
    url_size, = struct.unpack('<I', buf[4:8])
    _url = buf[8:(8 + url_size)].decode('ascii')
    data = buf[(8 + url_size):(8 + url_size + data_size)]
    return data


def _write_image(url: str, data: Buffer) -> str | None:
    file_hash = _hash_image(data)

    # Write the content to a file, using the hash to ensure uniqueness
    file_type = url.split('.')[-1].split('?')[0]
    if len(file_type) > 4:
        return None

    filename = f'{file_hash}.{file_type}'
    with open(filename, 'wb') as f:
        f.write(data)

    return filename


def _download_image(url: str, cache: dict[str, str]) -> tuple[str, str | None]:
    # First check to see if url is in cache
    urlhash = _url_hash(url)
    if urlhash in cache:
        file_data = _read_cacheline(cache[urlhash])
        filename = _write_image(url, file_data)
        if filename is None:
            return url, None

        info(f'Successfully retrieved {url} from the cache!')
        return url, filename

    try:
        # Send a GET request to the URL
        if not url.startswith('https://') and not url.startswith('http://'):
            url = 'http://' + url
        response = requests.get(url, headers={'User-agent': 'PyTower'})

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            filename = _write_image(url, response.content)
            if filename is None:
                return url, None

            info(f'{url} downloaded successfully.')

            return url, filename
        else:
            error(f"Failed to download {url}. Status code: {response.status_code}")
    except Exception as e:
        error(f"An error occurred: {e}")

    return url, None


class BackupIndex:
    """Data structure used internally to represent information about each backup"""
    original_path: str
    filename: str
    pytower_version: str
    resources: dict[str, str]

    def __init__(self, data: dict[str, Any] | None = None):
        if data is not None:
            try:
                self.original_path = data['original_path']
                self.filename = data['filename']
                self.pytower_version = data['pytower_version']
                self.resources = data['resources']
            except KeyError:
                self.resources = data
                self.pytower_version = '0.1.0'

    def to_dict(self):
        return vars(self)


async def _download_images(urls: Collection[str], install_dir: str, use_cache: bool=True):
    canvas_cache: dict[str, str] = {}
    if use_cache:
        # Try to locate canvas cache
        cache_path = os.path.join(os.path.join(os.path.join(install_dir, 'Tower'), 'Cache'), 'Canvas')
        if os.path.isdir(cache_path):
            subdirs = [os.path.join(cache_path, subdir) for subdir in os.listdir(cache_path)]
            subdirs = [d for d in subdirs if os.path.isdir(d)]
            for subdir in subdirs:
                cachelines = [os.path.join(subdir, f) for f in os.listdir(subdir)]
                cachelines = [f for f in cachelines if os.path.isfile(f)]
                for cacheline in cachelines:
                    md5_hash = os.path.basename(cacheline)[:-6]
                    canvas_cache[md5_hash] = cacheline
            success(f'Located {len(canvas_cache)} cached resources!')
        else:
            from .config import KEY_INSTALL_PATH
            error(f'Failed to locate canvas cache! Make sure Tower Unite install path is set in the config'
                  f' ({KEY_INSTALL_PATH})')

    results = await asyncio.gather(*[asyncio.to_thread(_download_image, url, canvas_cache) for url in urls])

    # Backed-up resources
    resources: dict[str, str] = {}
    for url, filename in results:
        if filename is not None:
            resources[url] = filename

    return resources


def make_backup(save: Suitebro) -> str:
    """
    Given a Suitebro save, creates a new backup

    Args:
        save: Suitebro object to make a backup of

    Returns:
        Path to backup directory, containing the save and its resource assets
    """
    # First make the folder for the backup
    save_name = save.filename

    # If save is just default "CondoData", use parent folder for name
    if save_name == 'CondoData':
        save_name = os.path.basename(save.directory)

    # Sanitize save_name a little more
    save_name = save_name.replace(' ', '-').strip()

    cur_time = datetime.datetime.now()
    timestamp = cur_time.strftime('%m-%d-%Y_%H%M%S')

    backup_path = os.path.join(BACKUP_DIR, f'{save_name}_{timestamp}')

    # Attach a suffix starting with _1 and incrementing upwards if the backup name already exists
    """
    while os.path.exists(backup_path):
        split = backup_path.split('_')
        suffix = split[-1]
        if '-' in suffix:
            backup_path = f'{backup_path}_1'
        else:
            backup_path = f"{''.join(split[:-1])}_{int(suffix)+1}"
    """

    os.makedirs(backup_path)

    # chdir to it
    old_cwd = os.getcwd()
    os.chdir(backup_path)

    # Gather all URLs
    urls = set[str]()

    def url_processor(dict_entry: list[Any] | dict[str, Any] | tuple[str, Any] | Any):
        if isinstance(dict_entry, tuple) and len(dict_entry) == 2:
            k, v = dict_entry
            if k == 'URL' or k == 'CanvasURL':
                urls.add(v['Str']['value'])

    for obj in save.objects:
        dict_walk(obj.item, url_processor)
        dict_walk(obj.properties, url_processor)

    # Process URLs further
    urls = {url.strip() for url in urls if url.strip() != ''}

    # Now that all the URLs have been added to urls set, download them all
    from .config import CONFIG
    install_dir = CONFIG.get(KEY_INSTALL_PATH)
    resources = asyncio.run(_download_images(urls, install_dir))

    # Create index and save to index.json
    save_suitebro(save, save.filename)

    index = BackupIndex()
    index.resources = resources
    index.pytower_version = __version__
    index.original_path = os.path.join(save.directory, save.filename)
    index.filename = save.filename

    with open('index.json', 'w') as fd:
        json.dump(index.to_dict(), fd, indent=2)

    success(f'Created backup at {os.path.relpath(backup_path, root_directory)}')
    info(f'To restore this backup, run the command: pytower backup restore {os.path.basename(backup_path)}')

    # Return to previous cwd
    os.chdir(old_cwd)

    return backup_path


def _resource_available(url: str) -> bool:
    try:
        # Use HEAD request for faster response
        response = requests.head(url, timeout=2, headers={'User-agent': 'PyTower'})
        if response.status_code == 200:
            debug(f"The website {url} is online and reachable.")
            return True
        else:
            debug(f"The website {url} is online but returned status code: {response.status_code}")
            return False
    except requests.ConnectionError:
        debug(f"The website {url} is unreachable.")
        return False
    except requests.Timeout:
        debug(f"Timeout occurred while trying to reach {url}.")
        return False
    except requests.RequestException as e:
        debug(f"An error occurred: {e}")
        return False


def _reachable_thread(url: str) -> bool:
    return _resource_available(url)


async def _check_links(urls: list[str]) -> set[str]:
    results = await asyncio.gather(*[asyncio.to_thread(_reachable_thread, url) for url in urls])
    return {url for (url, result) in zip(urls, results) if result}  # return set of urls online and 200 status


def restore_backup(path: str, force_reupload: bool=False, backend: ResourceBackend=CatboxBackend()):
    """
    Restores a backup from the backups folder

    Args:
        path: Path to the backup
        force_reupload: Whether to force reuploading files to backend
        backend: Backend to use (Catbox by default)
    """
    cwd = os.getcwd()
    os.chdir(path)
    with open('index.json', 'r') as fd:
        index = BackupIndex(json.load(fd))

    # First, handle reuploading files
    broken_files: list[str] = []
    available_urls = asyncio.run(_check_links(list(index.resources.keys())))
    for url, filename in index.resources.items():
        if url not in available_urls or force_reupload:
            broken_files.append(filename)

    info(f'Marked {len(broken_files)}/{len(index.resources.items())} resources for reupload')

    url_dict = backend.upload_files(broken_files)
    url_replacements: dict[str, str] = {}
    for url, filename in index.resources.items():
        if filename in url_dict:
            new_url = url_dict[filename]
            url_replacements[url] = new_url

    num_success = len(url_replacements)
    num_total = len(broken_files)
    if num_success > 0:
        level = WARNING_LEVEL_NUM
        if num_success == num_total:
            level = SUCCESS_LEVEL_NUM

        log(level, f'Reuploaded {len(url_replacements)}/{len(broken_files)} to {backend.name}!')
    elif num_total > 0:
        error('Failed to reupload any files :(')

    # Now get the backed-up save
    save = load_suitebro(index.filename)

    # Big URL replacement
    for old_url, new_url in url_replacements.items():
        params = ParameterDict({'replace': old_url, 'url': new_url})
        replace_url.main(save, Selection(save.objects), params)

    # Now save to original file location
    save_suitebro(save, index.original_path)

    os.chdir(cwd)


def fix_canvases(path: str, force_reupload: bool=False, backend: ResourceBackend=CatboxBackend()):
    save = load_suitebro(path)
    backup_path = make_backup(save)
    restore_backup(backup_path, force_reupload=force_reupload, backend=backend)