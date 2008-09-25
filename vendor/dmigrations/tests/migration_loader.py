from dmigrations.tests.common import *
from dmigrations.migration_loader import *
import os
import os.path

test_migrations_dir = os.path.join(
    os.path.realpath(os.path.dirname(__file__)), 'test_migrations'
)

class MigrationLoaderTest(TestCase):
    def test_valid_migration(self):
        "Valid migrations should load correctly"
        path = os.path.join(test_migrations_dir, 'valid_migration.py')
        migration = load_migration_from_path(path)
        self.assert_(isinstance(migration, BaseMigration))
    
    def test_valid_custom_migration(self):
        "Valid migrations using a custom subclass should load correctly"
        path = os.path.join(test_migrations_dir, 'valid_custom_migration.py')
        migration = load_migration_from_path(path)
        self.assert_(isinstance(migration, BaseMigration))
    
    def test_invalid_no_migrations(self):
        "Raise error if no migration found in a file"
        path = os.path.join(test_migrations_dir, 'invalid_no_migrations.py')
        self.assertRaises(BadMigrationError, load_migration_from_path, path)
    
    def test_invalid_migration_not_subclass(self):
        "Raise error if discovered migration does not subclass BaseMigration"
        path = os.path.join(test_migrations_dir, 'invalid_migration_not_subclass.py')
        self.assertRaises(BadMigrationError, load_migration_from_path, path)
    
    def test_migration_knows_file(self):
        "A migration should know which file it was loaded from"
        path = os.path.join(test_migrations_dir, 'valid_migration.py')
        migration = load_migration_from_path(path)
        self.assert_equal(migration.filepath, path)
        self.assert_equal(migration.name, 'valid_migration')
