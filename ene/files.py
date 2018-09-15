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
from typing import Iterable


from ene.database import Database

EXTENSIONS = ['.mkv',
              '.mp4',
              '.avi',
              '.m4v']


class FileManager:
    """
    Class to manage video files.
    """

    def __init__(self, cfg, data_home: Path):
        self.config = cfg
        self.dirs = [Path(x) for x in self.config.get('Local Paths', [])]
        self.db = Database(data_home / 'ene.db')
        self.series = defaultdict(list)

    def build_shows_from_db(self):
        """
        Fetches all shows from the database and adds them to the series
        dictionary without episode paths
        """
        shows = self.db.get_all_shows()
        for show in shows:
            self.series[show] = []

    def build_all_from_db(self):
        """
        Fetches all shows and episodes from the database and builds up the full
        dictionary of series
        """
        self.series.update(self.db.get_all())

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
                self.series[show].append(Path(episode))

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
        self.dirs = [Path(x) for x in self.config.get('Local Paths', [])]
        for directory in self.dirs:
            self.discover_episodes(directory)

    def refresh_single_show(self, show):
        """
        Looks for all the episodes of a given show and adds it to the list of
        episodes for that show

        Args:
            show:
                The show to search for all episodes of

        Returns:
            A list of new shows
        """
        res = []
        for directory in self.dirs:
            print(directory)
            print(type(directory))
            res.extend(self.find_episodes(show, directory))
        new = set(res) - set(self.series[show])
        self.series[show].extend(new)
        self.series[show].sort()
        return sorted(new)

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
                    episodes += self.find_episodes(name, path)
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
        op_or_ed = re.compile(r'(NCOP)|(NCED)|(\sOP[0-9]+)|(\sED[0-9]+)')
        for path, dirs, files in walk(directory):  # pylint: disable=W0612
            for file in files:
                episode = Path(file)
                if episode.suffix not in EXTENSIONS:
                    continue
                if op_or_ed.search(episode.name):
                    continue
                title = clean_title(episode.stem)
                self.series[title].append(path / episode)

    def get_readable_names(self, show: str) -> Iterable[str]:
        """
        Yields file names of a show

        Args:
            show: The show name

        Yields:
            The file names in the show
        """
        for path in self.series[show]:
            yield path.name

    def rename_show(self, old, new):
        """
        Renames a given show

        Args:
            old:
                The old name of the show
            new:
                The new name

        Returns:
            The episode list for the new show
        """
        self.series[new].append(self.series.pop(old))
        self.db.rename_show(old, new)
        return self.series[new]

    def delete_show(self, show):
        """
        Deletes a given show from the dictionary and the database

        Args:
            show:
                The show to remove
        """
        self.db.delete_show(show)
        self.series.pop(show)


def clean_title(title):
    """
    Removes things from a file name that are not part of the title

    Args:
        title:
            The original title to reformat

    Returns:
        The title of the series without extra things
    """
    # pull out a few common things that should not be part of a title
    # Adding detailed comments because coming back to regex after a break is confusing
    title = re.sub(r'[_,]', ' ', title)
    title = re.sub(r'\[[^]]*\]', '', title)  # Removes things between square brackets
    title = re.sub(r'\([^O)]*\)', '', title)  # Parenthesis
    title = re.sub(r'[sS]0?1', '', title)  # Remove season if its season one
    title = re.sub(r'^[0-9]+\.', '', title)  # Episode number at the beginning
    title = re.sub(r'[eE][pP]?[0-9]+.*', '', title)  # Anything after an episode number
    title = re.sub(r'-?\s+[0-9v]*\s*$', '', title)  # Removes trailing episode numbers
    title = re.sub(r'-\s(Episode)?\s?([0-9v])+.*', '', title)  # '- 08 - episode name
    title = re.sub(r'[sS]0?([2-9])', r'Season \1', title)  # Replace S02 with Season 2
    title = title.strip()
    return title


def _build_regex(name):
    pattern = '.*'
    title = name.split(' ')
    for word in title:
        pattern += word.lower()
        pattern += '.*'
    return re.compile(pattern)
