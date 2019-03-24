""" This module handles interactions with Show and Episode objects """
from ene.persistence.data_access import ShowDataAccess
from ene.entities import ShowList
from ene.files import FileManager


class SeriesManager:
    """
    Manages access to series
    """
    def __init__(self, config):
        self._series = ShowList()
        self._db = None
        self._config = config

    def init_db(self, data_home):
        """
        Initializes the connection to the SQLite database

        Args:
            data_home:
                Path to the SQLite database
        """
        self._db = ShowDataAccess()
        self._db.init_db(data_home)

    def get_shows_overview(self):
        """
        Gets a list of all shows and the number of episodes it has

        Returns:
            A tuple consisting of the show name and the number of episodes it has
        """
        for show in self._series.values():
            yield show.title, len(show)

    def get_episodes(self, show_name):
        """
        Gets all episodes for a given show

        Args:
            show_name:
                Show to get the episodes for

        Returns:
            A list of the shows available episodes
        """
        return self._series.get_episodes(show_name)

    def fetch_shows_from_db(self):
        """
        Fetches all shows from the database and adds them to the series list
        """

        for res in self._db.get_all_shows():
            self._series.add(res)

    def fetch_shows_from_files(self):
        """
        Fetches all shows from the configured file paths and adds them to
        the series list
        """
        file_manager = FileManager(self._config)
        file_manager.traverse_directories()
        for show in file_manager.series.values():
            self._series.add(show)

    def fetch_show_from_files(self, show_name):
        """
        Searches the configured files paths for a given show name and adds all
        results to the series list
        Args:
            show_name:
                The show name to search for
        """
        file_manager = FileManager(self._config)
        file_manager.refresh_single_show(show_name)
        for show in file_manager.series.values():
            self._series.add(show)

    def delete_show(self, show_name):
        """
        Deletes a given show from the series list and the database
        Args:
            show_name:
                The show name to remove
        """
        self._db.delete_show(self._series.pop(show_name))

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
        new_show = self._series[old].copy(True)
        new_show.title = new
        self._series.add(new_show)
        self.delete_show(old)
        self._db.save_show(new_show)

    def save_shows(self):
        """
        Persists the current series list to the database
        """
        self._db.save_show_list(self._series.values())
