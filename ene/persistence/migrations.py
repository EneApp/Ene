from datetime import datetime
from peewee import TextField
from playhouse.migrate import SqliteMigrator, migrate

from .models import VersionModel

DB_VERSION = 1

class Migrator:
    def __init__(self, db):
        self.db = db
        self.migrations = [self._migrate_from_0]

    def perform_migration(self, current_version):
        sqlite_migrator = SqliteMigrator(self.db.database)
        for i in range(current_version, DB_VERSION):
            self.migrations[i](sqlite_migrator)

    def _migrate_from_0(self, migrator):
        print('Performing database migration from version 0 to 1')
        with self.db.database.atomic():
            cover_image = TextField(null=True)
            migrate(
                migrator.add_column('Show', 'cover_image', cover_image)
            )
            VersionModel.get_or_create(version=1, migration_date=datetime.now())

def check_and_run_migrate(db):
    version_info = VersionModel.get_or_none()
    current_version = 0
    if not version_info:
        print('No version information found, assuming version 0')
    else:
        current_version = version_info.version

    if current_version < DB_VERSION:
        print(f'Ene database needs to be upgraded from version {current_version} to {DB_VERSION}')
        migrator = Migrator(db)
        migrator.perform_migration(current_version)
        print('Migration complete!')
