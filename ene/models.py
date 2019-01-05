from peewee import *
from ene.types_ import Episode, Show
from pathlib import Path

db = SqliteDatabase('./ene.db')


def table_name(table):
    return table.__name__.replace('Model', '')


class BaseModel(Model):
    class Meta:
        database = db
        table_function = table_name


class ShowModel(BaseModel):
    title = TextField()
    anilist_show_id = IntegerField(null=True)
    list_id = IntegerField(null=True)

    def to_show(self):
        episodes = EpisodeModel.select()\
            .join(ShowModel).where(EpisodeModel.show_id == self.id)
        episodes = set([x.to_episode() for x in episodes])
        return Show(self.title, self.anilist_show_id, self.list_id, episodes)

    @staticmethod
    def from_show(show: Show):
        return ShowModel(title=show.title, show_id=show.show_id, list_id=show.list_id)


class EpisodeModel(BaseModel):
    path = TextField()
    number = IntegerField()
    show = ForeignKeyField(ShowModel, backref='show_id')
    state = IntegerField()

    def to_episode(self):
        return Episode(Path(self.path), Episode.State(self.state), self.number)

    @staticmethod
    def from_episode(episode: Episode, show: ShowModel):
        return EpisodeModel(path=str(episode.path), number=episode.number, show=show, state=episode.state.value)


db.connect()
db.create_tables([ShowModel, EpisodeModel])