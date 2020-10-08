#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2020 Peijun Ma, Justin Sedge
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

"""This module contains the config class to hold config data"""
from collections import Mapping
from contextlib import contextmanager
from pathlib import Path

import toml


class Config(Mapping):
    """
    Class for config access
    """
    DEFAULT_CONFIG = {
    }

    def __init__(self, config_home: Path):
        """
        Create the config directory and files if they do not exist already

        Args:
            config_home: The configuration home directory
        """
        self.config_home = config_home
        self.config_home.mkdir(parents=True, exist_ok=True)

        self.config = self._read_config() if self.config_file.is_file() else {}
        self._old = None

        if not self.config:
            self.config = self.DEFAULT_CONFIG
            self.apply()

    @property
    def config_file(self) -> Path:
        """Returns the path of the config file"""
        return self.config_home / 'config.toml'

    def apply(self):
        """Writes the config in memory to file."""
        self._old = self.config.copy()
        with self.config_file.open('w+') as f:
            toml.dump(self.config, f)

    @contextmanager
    def change(self):
        """
        Context manager to make changes to config.

        Must call self.apply() within the scope to apply the changes.
        """
        self._old = self.config.copy()
        yield self.config
        self.config = self._old.copy()

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

    def __iter__(self):
        return iter(self.config)

    def __len__(self):
        return len(self.config)

    def get(self, key, default=None):
        """See Also: `dict.get`"""
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
