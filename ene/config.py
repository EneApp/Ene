#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018 Peijun Ma, Justin Sedge
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import MutableMapping
from pathlib import Path

import toml

CONFIG_DIR = Path.home() / '.config' / 'ene'


class Config(MutableMapping):
    """
    Class for config access
    """
    DEFAULT_CONFIG = {
    }

    def __init__(self):
        """
        Create the config directory and files if they do not exist already
        """
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        self.config = self._read_config() if self.config_file.is_file() else {}

        if not self.config:
            self.config = self.DEFAULT_CONFIG
            self._write_config()

    @property
    def config_file(self):
        return CONFIG_DIR / 'config.toml'

    def _write_config(self):
        """
        Writes the config in memory to file
        """
        with open(self.config_file, 'w+') as f:
            toml.dump(self.config, f)

    def _read_config(self) -> dict:
        """
        Reads the config from file
        Returns:
            dict containing the config
        """
        with open(self.config_file) as f:
            return toml.load(f)

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value
        self._write_config()

    def __delitem__(self, key):
        del self.config[key]
        self._write_config()

    def __iter__(self):
        return iter(self.config)

    def __len__(self):
        return len(self.config)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default