from sqlite3 import DatabaseError
from pathlib import Path

import pytest

from ene.database import Database
from . import HERE

MOCK_SQL = HERE / 'mock_db.sql'


@pytest.fixture
def empty_db():
    db = Database(Path(':memory:'))
    try:
        yield db
    finally:
        del db


@pytest.fixture
def mock_db():
    db = Database(Path(':memory:'))
    db.initial_setup()
    db.cursor.executescript(MOCK_SQL.read_text())
    yield db
    del db


def test_database_not_setup(empty_db):
    with pytest.raises(DatabaseError):
        empty_db.get_all()


def test_get_shows(mock_db):
    shows = ['foo', 'bar', 'baz']
    assert shows == mock_db.get_all_shows()
