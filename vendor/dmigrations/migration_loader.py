from migrations import BaseMigration
from exceptions import *

import imp
import os

def load_migration_from_path(file_path, dev=False):
    """
    Given a file_path to a 001_blah.py file, returns the migration object
    contained in that file. The file should have a "migration" symbol which
    is an instance of a BaseMigration subclass. Raise an error otherwise.
    """
    dir_name, file_name = os.path.split(file_path)
    
    mod_name = file_name.replace('.py', '')
    dot_py_suffix = ('.py', 'U', 1) # From imp.get_suffixes()[2]
    
    mod = imp.load_module(mod_name, open(file_path), file_path, dot_py_suffix)
    
    try:
        migration = mod.migration
    except AttributeError:
        raise BadMigrationError(
            u'Module %s has no migration instance' % file_path
        )
    
    if not isinstance(migration, BaseMigration):
        raise BadMigrationError(
            u'Migration %s is not a BaseMigration subclass' % file_path
        )
    
    # Set up .filepath and .name based on where it was loaded from
    migration.filepath = file_path
    migration.name = mod_name
    migration.dev = dev
    
    return migration
