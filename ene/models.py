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

"""This module handles data and data access."""
from pathlib import Path
import re
from enum import Enum
from peewee import Model, SqliteDatabase, TextField, IntegerField, ForeignKeyField

db = SqliteDatabase(None)


class EneDatabase:
    def __init__(self, path):
        """
        Initializes the Ene database, creating any tables as needed

        Args:
            path:
                The path where the Sqlite database file resides
        """
        self.database = db
        db.init(path)
        db.connect()
        db.create_tables([ShowModel, EpisodeModel])


def table_name(table):
    """
    Derives the database table name from the Peewee Model class

    Args:
        table:
            The model object referencing a table in the Ene database

    Returns:
        The name of the table it represents (strips "Model" from the name)
    """
    return table.__name__.replace('Model', '')


class BaseModel(Model):
    """
    Base model for all Ene models, provides base behaviour of the database
    and the table naming function
    """
    class Meta:
        """ Meta class for BaseModel which defines settings"""
        database = db
        table_function = table_name


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

    def add_episode(self, episode):
        """
        Adds a single episode to the shows set of episodes

        Args:
            episode: The episode to add
        """
        if episode in self.episodes:
            episode.state = self.episodes[episode].state

        self.episodes[episode] = episode

    def __len__(self):
        """
        The number of episodes in the show

        Returns:
            An integer representing the length of the episodes set
        """
        return len(self.episodes)


class ShowModel(BaseModel):
    """
    Model representing a Show in the database
    """
    title = TextField()
    anilist_show_id = IntegerField(null=True)
    list_id = IntegerField(null=True)

    @classmethod
    def from_show(cls, show: Show):
        return cls(title=show.title, anilist_show_id=show.show_id, list_id=show.list_id, id=show.key)

    def to_show(self):
        """
        Convert this model to a full Show object

        Returns:
            The Show object represented by this model
        """
        episodes = EpisodeModel.select() \
            .join(ShowModel).where(EpisodeModel.show_id == self.id)
        all_episodes = dict()
        for episode_model in episodes:
            episode = episode_model.to_episode()
            all_episodes[episode] = episode
        return Show(self.title, self.anilist_show_id, self.list_id, all_episodes, self.get_id())


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


class EpisodeModel(BaseModel):
    """ Model representing an Episode in the database"""
    path = TextField()
    number = IntegerField()
    show = ForeignKeyField(ShowModel, backref='show_id')
    state = IntegerField()

    @classmethod
    def from_episode(cls, episode: Episode, show: ShowModel):
        """
        Create a new model that represents the given Episode object

        Args:
            episode:
                The episode to build the Model for
            show:
                The show this Episode belongs to, required for the foreign key

        Returns:
            The newly created model representing the Episode
        """
        return cls(path=str(episode.path), number=episode.number, show=show,
                            state=episode.state.value)

    def to_episode(self):
        """
        Convert this model into a full Episode object

        Returns:
            The new Episode object represented by this model
        """
        return Episode(Path(self.path), Episode.State(self.state), self.number, self.get_id())


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
