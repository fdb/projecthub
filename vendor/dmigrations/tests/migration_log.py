from dmigrations.tests.common import *
from dmigrations.migration_state import MigrationState
from dmigrations.migration_db import MigrationDb
from dmigrations.migration_log import get_log
from datetime import datetime, date, time

class MigrationLogTest(TestCase):
  def set_up(self):
    from django.db import connection
    self.cursor = connection.cursor()

    for sql in [
      "DROP TABLE smigrations_schema",
      "DROP TABLE migrations",
      "DROP TABLE migrations_log",
      "CREATE TABLE mock (id INTEGER NOT NULL)"]:
      try: self.cursor.execute(sql)
      except: pass

  def tear_down(self):
    self.cursor.execute("DROP TABLE mock")

  def test_when_doing_something_then_loggged(self):
    db = MigrationDb(directory=self.mock_migrations_dir)
    db.warn = WarningsMocker()
    si = MigrationState(migration_db=db, dev=True)
    si.init()

    si.apply('001_foo')
    si.mark_as_unapplied('001_foo')
    si.apply('001_foo')
    si.mark_as_applied('005_omg')
    si.unapply('001_foo')

    self.assert_equal(
      [
        ("apply", "001_foo", "success"),
        ("mark_as_unapplied", "001_foo", "success"),
        ("apply", "001_foo", "success"),
        ("mark_as_applied", "005_omg", "success"),
        ("unapply", "001_foo", "success"),
      ], [row[:3] for row in get_log()]
    )
    self.assert_equal(True, isinstance(get_log()[0][3], datetime))
