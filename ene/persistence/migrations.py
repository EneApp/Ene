from .models import VersionModel

DB_VERSION = 0

class Migrator:
    def __init__(self, db):
        self.db = db
        self.migrations = [self._migrate_from_0]

    def perform_migration(self, current_version):
        for i in range(current_version, DB_VERSION):
            self.migrations[i]()

    def _migrate_from_0(self):
        print('Performing database migration from version 0 to 1')
        with self.db.database.atomic():
            pass

def migrate(db):
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
