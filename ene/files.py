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
from os import walk
from pathlib import Path
from ene.entities import Episode, ShowList


EXTENSIONS = ['.mkv',
              '.mp4',
              '.avi',
              '.m4v']


class FileManager:
    """
    Class to manage video files.
    """

    def __init__(self, cfg):
        self.config = cfg
        self.dirs = [Path(x) for x in self.config.get('Local Paths', [])]
        self.series = ShowList()

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
            res.extend(self.find_episodes(show, directory.iterdir()))
        new = set(res) - self.series.get_episodes(show)
        for new_show in new:
            self.series[show].add_episode(new_show)
        return sorted(new)

    def find_episodes(self, name, directory):
        """
        Finds all episodes in the set directory that match the given name

        Args:
            name: Name of the show to find episodes for
            directory: Directory to search in

        Returns:
            episodes: A list of all episodes found
        """
        regex = _build_regex(name)
        episodes = []
        for file in directory:
            path = Path(file)
            # check each file in the set directory
            if regex.match(path.name.lower()):
                if path.is_dir():
                    # if a folder matches the regex, assume it contains the episodes for that show
                    episodes += self.find_episodes(name, path)
                    break
                else:
                    # otherwise just append it to the list
                    episodes.append(Episode(path))
            elif path.is_dir() and self.config.get('Search Subfolders', default=False):
                # If folders are sorted differently, e.g. Ongoing/Winter 2018/Plan to Watch
                episodes += self.find_episodes(name, path)

        return sorted(episodes)

    def traverse_directories(self, directory=None):
        """
        Traverse one or more directories to locate all episodes.
        Can specify a specific directory to search, otherwise searches
        all configured directories

        Args:
            directory:
                The directory to traverse
        """
        if directory is None:
            folders = [Path(x) for x in self.config.get('Local Paths', [])]
        else:
            folders = [Path(directory)]
        for folder in folders:
            for path, dirs, files in walk(folder):  # pylint: disable=W0612
                self.discover_episodes(path, files)

    def discover_episodes(self, base_path, files):
        """
        Search through a directory to find all files which have a close enough
        name to be considered a part of the same series
        """
        op_or_ed = re.compile(r'(NCOP)|(NCED)|(\sOP[0-9]+)|(\sED[0-9]+)')
        for file in files:
            episode = Path(file)
            if episode.suffix not in EXTENSIONS:
                continue
            if op_or_ed.search(episode.name):
                continue
            title = clean_title(episode.stem)
            episode = Episode(base_path / episode)
            episode.parse_episode_number(title)
            self.series[title].add_episode(episode)


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
