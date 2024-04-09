import json
import os
import sys
from typing import Any

from .tower import root_directory


class TowerConfig:
    def __init__(self, filename):
        self.filename = filename
        self.path = os.path.join(root_directory, filename)
        self.config = self._load_config()
        self._save()

    def _load_config(self) -> dict:
        if not os.path.isfile(self.path):
            with open(self.path, 'w') as fd:
                fd.write('{}\n')

        with open(self.path, 'r') as fd:
            try:
                config = json.load(fd)
            except json.decoder.JSONDecodeError:
                config = {}

        # Get the default config
        default_install = r'"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Tower Unite"' if sys.platform == 'win32' \
            else os.path.join(os.path.expanduser('~'), '.local/share/steamapps/common/Tower Unite')

        default = json.loads(fr'''{{
            "tower_install_path": {default_install}
        }}''')

        # Assign any defaults not in config
        for key, d_value in default.items():
            if key not in config:
                config[key] = d_value

        return config

    def _save(self) -> None:
        with open(self.path, 'w') as fd:
            json.dump(self.config, fd, indent=2)

    def get(self, key) -> Any:
        return self.config[key]

    def set(self, key, value) -> None:
        if key not in self.config:
            raise ValueError

        self.config[key] = value
        self._save()

    def keys(self):
        return self.config.keys()

    def __getitem__(self, key):
        return self.config[key]
