from ene.database import Database
from pathlib import Path
from . import rmdir
from sqlite3 import DatabaseError

import pytest

DB_DIR = Path(__file__).parent / 'ene'
DB_PATH = DB_DIR / 'ene.eb'


@pytest.fixture
def empty_db():
    rmdir(DB_DIR, True)
    DB_DIR.mkdir(parents=True)
    db = Database(str(DB_PATH))
    yield db
    del db
    rmdir(DB_DIR, True)


def test_database_not_setup(empty_db):
    with pytest.raises(DatabaseError):
        empty_db.get_all()


