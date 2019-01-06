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


def init_db(path):
    """
    Initializes the Ene database, creating any tables as needed

    Args:
        path:
            The path where the Sqlite database file resides
    """
    # need to use global DB so that we can specify the database location at runtime
    global db
    db.init(path)
    db.connect()
    db.create_tables([Show.ShowModel, Episode.EpisodeModel])


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
    def __init__(self, title, show_id=None, list_id=None, episodes: set = None, model=None):
        self.title = title
        self.show_id = show_id
        self.list_id = list_id
        if episodes is None:
            self.episodes = set()
        else:
            self.episodes = episodes
        if model is None:
            self.model = Show.ShowModel(title=self.title,
                                        show_id=self.show_id,
                                        list_id=self.list_id)
        else:
            self.model = model

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

    class ShowModel(BaseModel):
        """
        Model representing a Show in the database
        """
        title = TextField()
        anilist_show_id = IntegerField(null=True)
        list_id = IntegerField(null=True)
        table = 'Show'

        def to_show(self):
            """
            Convert this model to a full Show object

            Returns:
                The Show object represented by this model
            """
            episodes = Episode.EpisodeModel.select() \
                .join(Show.ShowModel).where(Episode.EpisodeModel.show_id == self.id)
            episodes = {x.to_episode() for x in episodes}
            return Show(self.title, self.anilist_show_id, self.list_id, episodes, self)


class Episode:
    """ Represents a single episode from a show"""
    class State(Enum):
        """ Represents the watch state of an Episode"""
        NEW = 1
        UNWATCHED = 2
        WATCHED = 3

    def __init__(self, path: Path, state=State.NEW, number=0, model=None):
        self.path = path
        self.state = state
        self.name = path.name
        self.number = number
        self.model = model

    def populate_model(self, show: Show.ShowModel):
        """
        Create a new model that represents this Episode object

        Args:
            show:
                The show this Episode belongs to, required for the foreign key

        Returns:
            The newly created model representing the Episode
        """
        self.model = Episode.EpisodeModel(path=str(self.path), number=self.number, show=show,
                                          state=self.state.value)
        return self.model

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

    def update_state(self, new_state: State):
        """
        Update the Episode's watch state and persist the change in the database

        Args:
            new_state:
                The new state for the Episode
        """
        self.state = new_state
        self.model.state = new_state.value
        self.model.save()

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
        show = ForeignKeyField(Show.ShowModel, backref='show_id')
        state = IntegerField()
        table = 'Episode'

        def to_episode(self):
            """
            Convert this model into a full Episode object

            Returns:
                The new Episode object represented by this model
            """
            return Episode(Path(self.path), Episode.State(self.state), self.number, self)


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
