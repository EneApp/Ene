from pathlib import Path
import re


class Show:
    """
    Class containing information about a single show
    """
    def __init__(self, title, show_id=None, list_id=None, episodes: set = None):
        self.title = title
        self.show_id = show_id
        self.list_id = list_id
        if episodes is None:
            self.episodes = set()
        else:
            self.episodes = episodes

    def add_episode(self, episode):
        """
        Adds a single episode to the shows set of episodes

        Args:
            episode: The episode to add
        """
        self.episodes.add(episode)

    def __len__(self):
        """
        The number of episodes in the show

        Returns:
            An integer representing the length of the episodes set
        """
        return len(self.episodes)


class Episode:
    def __init__(self, path: Path, new=False):
        self.path = path
        self.watched = False
        self.new = new
        self.name = path.name
        self.number = 0

    def parse_episode_number(self, title):
        """
        Attempts to pull an episode number from the episodes file name given the
        show's title
        Args:
            title: The title of the show the episode belongs to
        """

        temp = self.name.replace(title, '')
        # Searches for a number that is not preceded by x or succeeded by x or p
        num = re.search(r'(?<![x0-9])[0-9]+(?![0-9xp])', temp)
        try:
            if num is not None:
                num = num[0]
                self.number = int(num)
            else:
                self.number = -1
        except ValueError:
            self.number = -1

    def __gt__(self, other):
        return self.number > other.number


class ShowList(dict):
    """
    A specialised dictionary for holding shows
    """
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
        return self[key].episodes
