from pathlib import Path
from sqlite3 import DatabaseError

import pytest

from ene.database import Database
from . import rmdir

DB_DIR = Path(__file__).parent / 'db'
DB_PATH = DB_DIR / 'ene.eb'


@pytest.fixture
def empty_db():
    rmdir(DB_DIR, True)
    DB_DIR.mkdir(parents=True)
    db = Database(str(DB_PATH))
    try:
        yield db
    finally:
        del db
        rmdir(DB_DIR, True)


def test_database_not_setup(empty_db):
    with pytest.raises(DatabaseError):
        empty_db.get_all()
