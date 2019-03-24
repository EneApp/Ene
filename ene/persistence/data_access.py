""" This module handles persistence of data to the database """
from .models import ShowModel, EpisodeModel, EneDatabase


class ShowDataAccess:
    """
    Contains methods to access and persist data to the SQLite database
    """
    def __init__(self):
        self.database = None

    def init_db(self, db_path):
        """
        Creates a connection to the SQLite database
        Args:
            db_path:
                The path that contains the database file
        """
        self.database = EneDatabase(str(db_path / 'ene.db'))

    @staticmethod
    def get_all_shows():
        """
        Fetches all shows from the database

        Yields:
            Show objects from the database
        """
        shows = ShowModel.select()
        for show_model in shows:
            yield show_model.to_show()

    def save_show_list(self, shows):
        """
        Saves a list of shows to the database
        Args:
            shows:
                List of shows to save
        """
        with self.database.database.atomic():
            for show in shows:
                self.save_show(show)

    def delete_show(self, show):
        """
        Deletes a given show and all of it's associated episodes
        Args:
            show:
                The Show object to delete from the database
        """
        show_model = ShowModel.from_show(show)
        show_model.delete_instance()
        for episode in show.episodes:
            self.delete_episode(episode, show_model)

    @staticmethod
    def delete_episode(episode, parent_show):
        """
        Deletes a given episode from the database
        Args:
            episode:
                The Episode object to delete
            parent_show:
                The Show the episode belongs to
        """
        episode_model = EpisodeModel.from_episode(episode, parent_show)
        episode_model.delete_instance()

    def save_show(self, show):
        """
        Saves a given show and all of it's episodes
        Args:
            show:
                The Show object to save
        """
        show_model = ShowModel.from_show(show)
        show_model.save()
        show.key = show_model.id
        for episode in show.episodes:
            self.save_episode(episode, show_model)

    @staticmethod
    def get_show_from_episode(episode):
        return ShowModel.select().join(EpisodeModel).where(EpisodeModel.id == episode.key).get()

    def save_episode(self, episode, parent_show=None):
        """
        Saves a given episode to the database
        Args:
            episode:
                The Episode object to save
            parent_show:
                The Show that the episode belongs to
        """
        if parent_show is None:
            parent_show = self.get_show_from_episode(episode)
        episode_model = EpisodeModel.from_episode(episode, parent_show)
        episode_model.save()
        episode.key = episode_model.id
