from sqlite3 import DatabaseError

import pytest

from ene.database import Database
from . import DATA_HOME, rmdir

DB_PATH = DATA_HOME / 'ene.db'


@pytest.fixture
def empty_db():
    rmdir(DATA_HOME, True)
    DATA_HOME.mkdir(parents=True)
    db = Database(DATA_HOME)
    try:
        yield db
    finally:
        del db
        rmdir(DATA_HOME, True)


def test_database_not_setup(empty_db):
    DB_PATH.touch()
    with pytest.raises(DatabaseError):
        empty_db.get_all()
