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

from pathlib import Path
import re
import ene.config


class FileManager:

    def __init__(self, cfg):
        self.config = cfg
        self.dir = Path(self.config.get('Local Files', default=Path.home() / 'Videos'))

    def set_dir(self, path):
        self.dir = Path(path)

    def find_episodes(self, name, directory=None):
        """
        Finds all episodes in the set directory that match the given name
        Args:
            name: Name of the show to find episodes for
            directory: None for default directory, otherwise searches a subfolder

        Returns:
            episodes: A list of all episodes found
        """
        regex = self._build_regex(name)
        if directory is None:
            directory = self.dir
        episodes = []
        for path in directory.iterdir():
            # check each file in the set directory
            if regex.match(path.name.lower()):
                if path.is_dir():
                    # if a folder matches the regex, assume it contains the episodes for that show
                    episodes = self.find_episodes(name, path)
                    break
                else:
                    # otherwise just append it to the list
                    episodes.append(path)
            elif path.is_dir() and self.config.get('Search Subfolders', default=False):
                # If folders are sorted differently, e.g. Ongoing/Winter 2018/Plan to Watch
                episodes += self.find_episodes(name, path)

        return episodes

    def _build_regex(self, name):
        pattern = '.*'
        title = name.split(' ')
        for word in title:
            pattern += word.lower()
            pattern += '.*'
        return re.compile(pattern)
