""" This module handles series related objects """
import re
from enum import Enum
from pathlib import Path
from copy import deepcopy


class Show:
    """
    Class containing information about a single show
    """
    def __init__(self, title, show_id=None, list_id=None, episodes: dict = None, key=None):
        self.title = title
        self.show_id = show_id
        self.list_id = list_id
        if episodes is None:
            self.episodes = dict()
        else:
            self.episodes = episodes
        self.key = key

    def add_or_update_episode(self, episode):
        """
        Adds a single episode to the shows set of episodes
        or updates the episode number if it already exists

        Args:
            episode: The episode to add
        """
        if episode in self.episodes:
            self.episodes[episode].number = episode.number
        else:
            self.episodes[episode] = episode

    def merge(self, other):
        """
        Merges the given show with this one

        Args:
            other:
                The other Show object to merge with this one
        """
        for episode in other.episodes:
            self.add_or_update_episode(episode)

    def __len__(self):
        """
        The number of episodes in the show

        Returns:
            An integer representing the length of the episodes set
        """
        return len(self.episodes)


class Episode:
    """ Represents a single episode from a show"""
    class State(Enum):
        """ Represents the watch state of an Episode"""
        NEW = 1
        UNWATCHED = 2
        WATCHED = 3

    def __init__(self, path: Path, state=State.NEW, number=0, key=None):
        self.path = path
        self.state = state
        self.name = path.name
        self.number = number
        self.key = key

    def parse_episode_number(self, title):
        """
        Attempts to pull an episode number from the episodes file name given the
        show's title

        Args:
            title: The title of the show the episode belongs to
        """

        temp = self.name.replace(title, '')
        # Searches for a number that is not preceded by x or succeeded by x or p
        num = re.search(r'(?<![\(x0-9])[0-9]+(?![0-9xp])', temp)
        try:
            if num is not None:
                num = num[0]
                self.number = int(num)
            else:
                self.number = -1
        except ValueError:
            self.number = -1

    def update_state(self, new_state: State):
        """
        Update the Episode's watch state

        Args:
            new_state:
                The new state for the Episode
        """
        self.state = new_state

    def __gt__(self, other):
        return self.number > other.number

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return hash(self.path)


class ShowList(dict):
    """
    A specialised dictionary for holding shows
    """
    def add(self, show):
        """
        Adds the given show to the list, if the show is already in the list
        then the two are merged
        Args:
            show:
                The Show object to add to the list
        """
        if show.title not in self:
            self[show.title] = show
        else:
            self[show.title].merge(show)

    def __missing__(self, key):
        """
        Called when an accessed element is not in the dict.
        Creates a new show with the given key as its title
        Args:
            key: The key of the element that was accessed

        Returns:
            The newly created show with title key
        """
        self[key] = Show(key)
        return self[key]

    def get_episodes(self, key):
        """
        Get episodes for the show given by key
        Functions similar to list[key].episodes

        Args:
            key:
                The show to fetch episodes for

        Returns:
            Episodes for for the given show
        """
        return self[key].episodes
