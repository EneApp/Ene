from itertools import chain
from sqlite3 import DatabaseError
from pathlib import Path

import pytest

from ene.database import Database
from . import HERE

MOCK_SQL = HERE / 'mock_db.sql'
MOCK_SHOWS = {
        'foo': ['foo episode 1',
                'foo episode 2',
                'foo episode 3',
                'foo episode 4',
                'foo episode 5'],
        'bar': ['bar episode 1',
                'bar episode 2',
                'bar episode 3'],
        'baz': ['baz episode 1',
                'baz episode 2',
                'baz episode 3',
                'baz episode 4']
    }


@pytest.fixture
def empty_db() -> Database:
    db = Database(Path(':memory:'))
    db.initial_setup()
    yield db
    del db


@pytest.fixture
def mock_db() -> Database:
    db = Database(Path(':memory:'))
    db.initial_setup()
    db.cursor.executescript(MOCK_SQL.read_text())
    yield db
    del db


def test_get_shows(mock_db):
    assert list(MOCK_SHOWS.keys()) == mock_db.get_all_shows()


def test_get_show_by_name(mock_db):
    assert mock_db.get_show_id_by_name('foo') == 1
    assert mock_db.get_show_id_by_name('bar') == 2
    assert mock_db.get_show_id_by_name('baz') == 3


def test_get_nonexistent_show(mock_db):
    assert mock_db.get_show_id_by_name('quz') is None


def test_get_episodes_for_show(mock_db):
    for show in MOCK_SHOWS:
        assert mock_db.get_episodes_by_show_name(show) == MOCK_SHOWS[show]


def test_get_all(mock_db):
    assert mock_db.get_all() == MOCK_SHOWS


def test_get_episodes(mock_db):
    assert mock_db.get_all_episodes() == list(chain.from_iterable(MOCK_SHOWS.values()))


def test_write_show(empty_db):
    assert empty_db.add_show('foo') == 1
    assert empty_db.get_show_id_by_name('foo') == 1


def test_write_episode(empty_db):
    assert empty_db.add_episode_by_show_name('foo episode 1', 'foo') == 1
    assert empty_db.get_show_id_by_name('foo') == 1
    assert empty_db.get_episodes_by_show_name('foo') == ['foo episode 1']


@pytest.mark.xfail
def test_write_all_episodes(empty_db):
    empty_db.write_all_episodes_delta(MOCK_SHOWS)
    assert MOCK_SHOWS == empty_db.get_all()
