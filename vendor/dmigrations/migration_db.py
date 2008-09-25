from migration_loader import load_migration_from_path
from exceptions import *

import os, sys
import re

class MigrationDb(object):
    
    def __init__(self, directory=None, migrations=None):
        self.directory = directory
        self._migrations = migrations
    
    @property
    def migrations(self):
        """
        Lazy migrations property. Mostly to make overriding in tests easier.
        """
        if self._migrations == None:
            self.populate_migrations_from_directory()
        
        return self._migrations
    
    def populate_migrations_from_ls(self, ls):
        """
        Populate a list of migrations based on directory listing.
        Separate from populate_migrations_from_directory for easier testing.
        """
        self._migrations = [
            re.sub(r'\.py$', '', file_name) 
            for file_name in ls 
            if re.search(r'^\d+_.*\.py$', file_name)
        ]
        self.warn_if_duplicate_migration_numbers()
    
    def migration_number(self, migration):
        """
        Return migration number based on migration name like <int>_<anything>
        """
        m = re.search(r'(\d+)_', migration)
        if m:
            return int(m.group(1))
        else:
            raise Exception(u"%s is not a valid migration name" % migration)
    
    def migration_sort_key(self, migration):
        """
        Return sort key for migrations - by number first, then by ascii.
        """
        return (self.migration_number(migration), migration)
    
    def sort_migrations(self, migration_list):
        """
        Return sorted list of migrations.
        """
        return sorted(migration_list, key=self.migration_sort_key)
    
    def warn_if_duplicate_migration_numbers(self):
        """
        Warn if there are multiple migrations with the same number.
        This situation is explicitly SUPPORTED, so it's not an error,
        but more likely than not it's not what you want to do.
        """
        by_number = {}
        
        for migration_name in self.migrations:
            i = self.migration_number(migration_name)
            by_number.setdefault(i, [])
            by_number[i].append(migration_name)
        
        for number in sorted(by_number.keys()):
            if len(by_number[number]) > 1:
                self.warn(
                    u"There are multiple migrations with the same number "
                     "%d: %s" % (number, ", ".join(
                        sorted(by_number[number])
                    ))
                )
    
    def warn(self, warning):
        """
        Print warning.
        Separate function for easy testing.
        """
        print >>sys.stderr, u"Warning: %s" % warning
    
    def populate_migrations_from_directory(self):
        """
        Populate list of migrations based on self.directory.
        """
        if self.directory == None:
            self.populate_migrations_from_ls([])
        else:
            self.populate_migrations_from_ls(os.listdir(self.directory))
    
    def list(self):
        """
        Return ordered list of migrations in the database.
        """
        return self.sort_migrations(self.migrations)
    
    def is_dev_migration(self, name):
        """
        Migration is a DEV migration if it has string "_DEV_" in its name.
        """
        return bool(re.search(r'_DEV_', name))
    
    def find_unique_migration_by_number(self, number):
        matching_migrations = [
            name for name in self.migrations 
            if self.migration_number(name) == number
        ]
        
        if len(matching_migrations) == 0:
            return None
        elif len(matching_migrations) == 1:
            return matching_migrations[0]
        else:
            raise AmbiguousMigrationNameError(number)
  
    def force_resolve_migration_name(self, name):
        """
        Take either full name or a number, and return full name for an 
        existing migration.
        """
        if name in self.migrations:
            return name
        elif re.search(r'^\d+$', str(name)):
            resolved_migration_name = self.find_unique_migration_by_number(
                int(name)
            )
            if resolved_migration_name is None:
                raise NoSuchMigrationError(name)
            else:
                return resolved_migration_name
        else:
            raise NoSuchMigrationError(name)
    
    def resolve_migration_path(self, name):
        """
        Return path for existing migration name.
        """
        name = self.force_resolve_migration_name(name)
        return os.path.join(self.directory, name + ".py")
    
    def migration_path(self, name):
        """
        Return path for new migration name.
        """
        number = 1 + max([0] + [
            self.migration_number(migration) for migration in self.migrations
        ])
        
        return u"%s/%03d_%s.py" % (self.directory, number, name)
    
    def load_migration_object(self, name):
        """
        Get migration with given name or number.
        """
        
        name = self.force_resolve_migration_name(name)
        full_path = self.resolve_migration_path(name)
        dev = self.is_dev_migration(name)
        
        return load_migration_from_path(full_path, dev=dev)
