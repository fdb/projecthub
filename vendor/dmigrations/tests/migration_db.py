from common import *
from dmigrations.migration_db import MigrationDb

import os

class MigrationDbTest(TestCase):
  def set_up(self):
    self.mock_migrations_dir = os.path.join(os.path.dirname(__file__), "mock_migrations_dir")

  def test_migrations_sorted_by_numbers_not_ascii(self):
    db = MigrationDb(migrations=[
      "04_blah",
      "03_blah",
      "002_bar",
      "12_blah",
      "01_foo",
      "011_blah",
    ])
    self.assert_equal([
        "01_foo",
        "002_bar",
        "03_blah",
        "04_blah",
        "011_blah",
        "12_blah",
      ], db.list()
    )

  def test_migrations_can_be_initialized_from_directory(self):
    db = MigrationDb(directory=self.mock_migrations_dir)
    db.warn = WarningsMocker()
    
    self.assert_equal([
        "001_foo",
        "002_bar",
        "005_DEV_hello",
        "009_one",
        "09_two",
      ], db.list()
    )

  def test_dups_and_missing_numbers_ok(self):
    db = MigrationDb(migrations = [
      "9_sweet",
      "8_blah_one",
      "7_blah",
      "10_gah",
      "8_blah_three",
      "1_foo",
      "8_blah_two",
    ])
    self.assert_equal([
        "1_foo",
        "7_blah",
        "8_blah_one",
        "8_blah_three",
        "8_blah_two",
        "9_sweet",
        "10_gah",
      ], db.list()
    )
    
  def test_nonpy_and_nonnumber_are_ignored(self):
    db = MigrationDb()
    db.populate_migrations_from_ls(["1_foo.py", "1_bar.pyc", "4-ohhi.py", "-9_kitty.py", "1_bar.html", ".", ".boo", "..", "123.py.gz", "hello_45.py", "__init__.py", "___init__.pyc", "hello.py", "hello.pyc"])
    self.assert_equal([
         "1_foo",
      ], db.list()
    )

  def test_dup_warnings(self):
    db = MigrationDb()
    db.warn = WarningsMocker()
    db.populate_migrations_from_ls([
      "17_foo.py",
      "017_bar.py",
      "0018_foo.py",
      "00018_foo.py",
      "180_hello.py",
    ])
    self.assert_equal(
      [
      u'There are multiple migrations with the same number 17: 017_bar, 17_foo',
      u'There are multiple migrations with the same number 18: 00018_foo, 0018_foo'
      ],
      db.warn.warnings
    )

  def test_is_dev_migration(self):
    db = MigrationDb()
    self.assert_equal(False, db.is_dev_migration("1_foo"))
    self.assert_equal(False, db.is_dev_migration("1DEV_foo"))
    self.assert_equal(False, db.is_dev_migration("1_DEVELOPER_foo"))

    self.assert_equal(True, db.is_dev_migration("1_DEV_foo"))
    self.assert_equal(True, db.is_dev_migration("005_DEV_bar"))
    self.assert_equal(True, db.is_dev_migration("1__DEV__foo"))

  def test_load_migration_object(self):
    db = MigrationDb(directory=self.mock_migrations_dir)
    db.warn = WarningsMocker()

    for name in ['001_foo', '0001', '001', '01', '1', 1]:
      self.assert_attrs(db.load_migration_object(name),
        name = '001_foo',
        dev = False,
        sql_up = "INSERT INTO mock VALUES (1)",
      )

    for name in ['002_bar', '0002', '002', '02', '2', 2]:
      self.assert_attrs(db.load_migration_object(name),
        name = '002_bar',
        dev = False,
        sql_up = "INSERT INTO mock VALUES (2)",
      )

    for name in ['005_DEV_hello', '0005', '005', '05', '5', 5]:
      self.assert_attrs(db.load_migration_object(name),
        name = '005_DEV_hello',
        dev = True,
        sql_up = "INSERT INTO mock VALUES (5)",
      )

    for name in ['3', '02_foo', '2_foo', 3]:
      self.assert_raises(NoSuchMigrationError, lambda: db.load_migration_object(name))

  def test_load_migration_object_with_dups(self):
    db = MigrationDb(directory=self.mock_migrations_dir)
    db.warn = WarningsMocker()

    self.assert_attrs(db.load_migration_object('009_one'),
      name = '009_one',
      dev = False,
      sql_up = "INSERT INTO mock VALUES (9, 1)",
    )

    self.assert_attrs(db.load_migration_object('09_two'),
      name = '09_two',
      dev = False,
      sql_up = "INSERT INTO mock VALUES (9, 2)",
    )

    for name in ['0009', '009', '09', '9', 9]:
      self.assert_raises(AmbiguousMigrationNameError, lambda: db.load_migration_object(name))

  def test_find_unique_migration_by_number(self):
    db = MigrationDb(directory=self.mock_migrations_dir)
    db.warn = WarningsMocker()

    self.assert_equal("001_foo", db.find_unique_migration_by_number(1))
    self.assert_equal("002_bar", db.find_unique_migration_by_number(2))
    self.assert_equal(None, db.find_unique_migration_by_number(3))
    self.assert_raises(AmbiguousMigrationNameError, lambda: db.find_unique_migration_by_number(9))

  def test_migration_path(self):
    db = MigrationDb(directory=self.mock_migrations_dir)
    db.warn = WarningsMocker()
    
    self.assert_equal(self.mock_migrations_dir + '/010_foo.py', db.migration_path('foo'))
