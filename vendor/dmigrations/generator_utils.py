from dmigrations.migration_db import MigrationDb
from django.conf import settings

def save_migration(output, migration_output, app_name):
    """
    If output flag is set, print migration out.
    Else save it to disk.
    """
    if output:
        print migration_output
    else:
        file_path = MigrationDb(
            directory = settings.DMIGRATIONS_DIR
        ).migration_path(app_name)
        open(file_path, 'w').write(migration_output)
        print "Created migration: %s" % file_path
