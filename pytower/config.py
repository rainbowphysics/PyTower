import json
import os
import sys
from typing import Any, Callable

from . import root_directory

KEY_INSTALL_PATH = 'tower_install_path'
KEY_IMGUR_CLIENT_ID = 'imgur_client_id'
KEY_CATBOX_USERHASH = 'catbox_userhash'
KEY_FROM_SOURCE = 'from_source'


class TowerConfig:
    def __init__(self, filename):
        self.filename = filename
        self.path = os.path.join(root_directory, filename)
        self.config = self._load_config()
        self._save()

        global CONFIG
        CONFIG = self

    def _load_config(self) -> dict:
        # Create empty .json if need to
        if not os.path.isfile(self.path):
            with open(self.path, 'w') as fd:
                fd.write('{}\n')

        # Try to load config
        with open(self.path, 'r') as fd:
            try:
                config = json.load(fd)
            except json.decoder.JSONDecodeError:
                config = {}

        default_install = r'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Tower Unite' if sys.platform == 'win32' \
            else os.path.join(os.path.expanduser('~'), '.local/share/steamapps/common/Tower Unite')

        # Get the default config
        default = json.loads(fr'''{{
            "{KEY_INSTALL_PATH}": "{default_install}",
            "{KEY_IMGUR_CLIENT_ID}": null,
            "{KEY_CATBOX_USERHASH}": null,
            "{KEY_FROM_SOURCE}": false
        }}''')

        # Assign any defaults not in config
        for key, d_value in default.items():
            if key not in config:
                config[key] = d_value

        return config

    def _save(self) -> None:
        with open(self.path, 'w') as fd:
            json.dump(self.config, fd, indent=2)

    def get(self, key: str, dtype: Callable[[Any], Any] | None = None) -> Any:
        entry = self.config[key]
        if dtype is not None and entry is not None:
            entry = dtype(entry)
        return entry

    def set(self, key, value) -> None:
        if key not in self.config:
            raise ValueError

        self.config[key] = value
        self._save()

    def keys(self):
        return self.config.keys()

    def __getitem__(self, key):
        return self.config[key]


CONFIG: TowerConfig | None = None
