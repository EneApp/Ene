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

"""This module handles local video files."""

import re
from collections import defaultdict
from os import walk
from pathlib import Path

from fuzzywuzzy import fuzz

from ene.constants import DATA_HOME
from ene.database import Database


class FileManager:
    """
    Class to manage video files.
    """

    def __init__(self, cfg):
        self.config = cfg
        self.dirs = self.config.get('Local Paths', default=[Path.home() / 'Videos'])
        self.db = Database(self.config.get('Database Path', default=DATA_HOME / 'ene.db'))
        self.series = defaultdict(list)

    def build_shows_from_db(self):
        """
        Fetches all shows from the database and adds them to the series
        dictionary without episode paths
        """
        shows = self.db.get_all_shows()
        for show in shows:
            self.series[show[0]] = []

    def build_all_from_db(self):
        """
        Fetches all shows and episodes from the database and builds up the full
        dictionary of series
        """
        shows = self.db.get_all()
        for show in shows:
            self.series[show[0]].append(Path(show[1]))

    def fetch_db_episodes_for_show(self, show):
        """
        Fetches all the episodes for a given show from the database and adds
        them to the episode list for that show in the dictionary

        Args:
            show:
                The show to fetch episodes for
        """
        if len(self.series[show]) is 0:
            episodes = self.db.get_episodes_by_show_name(show)
            episodes.sort()
            for episode in episodes:
                self.series[show].append(Path(episode[0]))

    def dump_to_db(self):
        """
        Dumps the current dictionary to the database
        """
        self.db.write_all_shows_delta(self.series.keys())
        self.db.write_all_episodes_delta(self.series)

    def refresh_shows(self):
        """
        Discovers episodes from each path defined in the config and tidies up
        their titles
        """
        for directory in self.dirs:
            self.discover_episodes(directory)
        self.series = clean_titles(self.series)

    def find_episodes(self, name, directory):
        """
        Finds all episodes in the set directory that match the given name

        Args:
            name: Name of the show to find episodes for
            directory: None for default directory, otherwise searches a sub folder

        Returns:
            episodes: A list of all episodes found
        """
        regex = _build_regex(name)
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

    def discover_episodes(self, directory):
        """
        Search through a directory to find all files which have a close enough
        name to be considered a part of the same series
        """
        for path, dirs, files in walk(directory):  # pylint: disable=W0612
            for file in files:
                matched = False
                for show in self.series:
                    if fuzz.token_set_ratio(show, file) > 90:
                        self.series[show].append(Path(path) / file)
                        matched = True
                        break
                if not matched:
                    self.series[file].append(Path(path) / file)

    def get_readable_names(self, show):
        return [x.name for x in self.series[show]]


def clean_titles(series):
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
        title = re.sub(r'-\s*[0-9v]*\s*$', '', title)  # Removes trailing episode numbers

        if title == '':
            title = key

        updated_titles[key] = title

    for old, new in updated_titles.items():
        # Then go through and replace the old with the new
        series[new].extend(series.pop(old))
    return series


def _build_regex(name):
    pattern = '.*'
    title = name.split(' ')
    for word in title:
        pattern += word.lower()
        pattern += '.*'
    return re.compile(pattern)
