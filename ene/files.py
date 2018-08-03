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

import re
from collections import defaultdict
from os import walk
from pathlib import Path

from fuzzywuzzy import fuzz


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

    def discover_episodes(self):
        """
        Search through a directory to find all files which have a close enough
        name to be considered a part of the same series
        Returns:
            A dictionary with the series name as a key and a list of episodes
            in that series
        """
        series = defaultdict(list)
        for path, dirs, files in walk(self.dir):
            for file in files:
                matched = False
                for show in series:
                    if fuzz.token_set_ratio(show, file) > 90:
                        series[show].append(Path(path) / file)
                        matched = True
                        break
                if not matched:
                    series[file].append(Path(path) / file)
        series = self.clean_titles(series)
        return series

    def clean_titles(self, series):
        """
        Attempts to clean up the title in the series dictionary by comparing
        the names of two files
        Args:
            series:
                A dictionary with the series name as a key and a list of files
        Returns:
            A dictionary with a slightly more well formatted name
        """
        updated_titles = defaultdict(str)
        for key, item in series.items():
            # First iterate through the list to find title that can be updated
            if len(item) > 1:
                # Split both names on commas, underscores and whitespace
                name_a = re.split(r'[,_\s]', key)
                name_b = re.split(r'[,_\s]', item[1].name)

                title = ' '.join(x for x in name_a if x in name_b)
            else:
                # When we can't compare to a similar title, just remove the same as above
                title = re.sub(r'[,_\s]', ' ', key)
            # pull out a few common things that should not be part of a title
            # Adding detailed comments because coming back to regex after a break is confusing
            title = re.sub(r'\[[^]]*\]', '', title)  # Removes things between square brackets
            title = re.sub(r'\..*$', '', title)  # Removes file extensions
            title = re.sub(r'-\s[0-9v]*\s*$', '', title)  # Removes trailing episode numbers

            if title == '':
                title = key

            updated_titles[key] = title

        for old, new in updated_titles.items():
            # Then go through and replace the old with the new
            series[new].extend(series.pop(old))
        return series

    def _build_regex(self, name):
        pattern = '.*'
        title = name.split(' ')
        for word in title:
            pattern += word.lower()
            pattern += '.*'
        return re.compile(pattern)
