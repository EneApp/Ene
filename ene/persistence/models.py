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

"""This module handles data persistence models."""
from pathlib import Path
from peewee import Model, SqliteDatabase, TextField, IntegerField, ForeignKeyField

from ene.entities import Show, Episode

db = SqliteDatabase(None)


class EneDatabase:
    """
    Contains information about the Ene SQLite database
    """
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


class ShowModel(BaseModel):
    """
    Model representing a Show in the database
    """
    title = TextField(unique=True)
    anilist_show_id = IntegerField(null=True)
    list_id = IntegerField(null=True)

    @classmethod
    def from_show(cls, show: Show):
        """
        Create a new ShowModel from the given Show object

        Args:
            show:
                The Show object to build the ShowModel for

        Returns:
            The newly created ShowModel object
        """
        return cls(title=show.title, anilist_show_id=show.show_id, list_id=show.list_id,
                   id=show.key)

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


class EpisodeModel(BaseModel):
    """ Model representing an Episode in the database"""
    path = TextField()
    number = IntegerField()
    show = ForeignKeyField(ShowModel, backref='show_id')
    state = IntegerField()

    @classmethod
    def from_episode(cls, episode: Episode, show: ShowModel):
        """
        Create a new EpisodeModel that represents the given Episode object

        Args:
            episode:
                The episode to build the EpisodeModel for
            show:
                The show this Episode belongs to, required for the foreign key

        Returns:
            The newly created model representing the Episode
        """
        return cls(path=str(episode.path), number=episode.number, show=show,
                   state=episode.state.value, id=episode.key)

    def to_episode(self):
        """
        Convert this model into a full Episode object

        Returns:
            The new Episode object represented by this model
        """
        return Episode(Path(self.path), Episode.State(self.state), self.number, self.get_id())
