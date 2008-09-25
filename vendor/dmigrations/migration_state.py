from django.db import connection
from exceptions import *
import re

def _execute(*sql):
    cursor = connection.cursor()
    cursor.execute(*sql)
    return cursor

def _execute_in_transaction(*sql):
    cursor = connection.cursor()
    cursor.execute("BEGIN")
    cursor.execute(*sql)
    cursor.execute("COMMIT")

def table_present(table_name):
    cursor = _execute("SHOW TABLES LIKE %s", [table_name])
    return bool(cursor.fetchone())

def _up(migrations):
    return [(m, 'up') for m in migrations]

def _down(migrations):
    return [(m, 'down') for m in migrations]

class MigrationState(object):
    
    def __init__(self, dev=None, migration_db=None):
        self.migration_db = migration_db
        self.dev = dev
    
    def migration_table_present(self):
        return table_present('dmigrations')
    
    def log(self, action, migration_name, status='success'):
        from migration_log import log_action
        log_action(action, migration_name, status)
    
    def applied_but_not_in_db(self):
        migrations_in_db = set(self.migration_db.list())
        applied_migrations = [
            m[0] for m in _execute(
                "SELECT migration FROM dmigrations"
            ).fetchall()
        ]
        return self.migration_db.sort_migrations(
            [m for m in applied_migrations if m not in migrations_in_db]
        )
      
    def apply(self, name):
        try:
            migration = self.migration_db.load_migration_object(name)
            migration.up()
            self.mark_as_applied(name, log=False)
            self.log('apply', name)
        except Exception, e:
            self.log('apply', name, str(e))
            raise
    
    def unapply(self, name):
        try:
            migration = self.migration_db.load_migration_object(name)
            migration.down()
            self.mark_as_unapplied(name, log=False)
            self.log('unapply', name)
        except Exception, e:
            self.log('unapply', name, str(e))
            raise
    
    def mark_as_applied(self, name, log=True):
        if not self.is_applied(name):
            _execute_in_transaction(
                "INSERT INTO dmigrations (migration) VALUES (%s)", [name]
            )
        if log:
            self.log('mark_as_applied', name)
    
    def mark_as_unapplied(self, name, log=True):
        if self.is_applied(name):
            _execute_in_transaction(
                "DELETE FROM dmigrations WHERE migration = %s", [name]
            )
        if log:
            self.log('mark_as_unapplied', name)
      
    def is_applied(self, name):
        cursor = _execute(
            "SELECT * FROM dmigrations WHERE migration = %s", [name]
        )
        return bool(cursor.fetchone())
    
    def all_migrations_applied(self):
        cursor = _execute("SELECT migration FROM dmigrations")
        return self.migration_db.sort_migrations(
            [row[0] for row in cursor.fetchall()]
        )
    
    def create_migration_table(self):
        create_new = """
            CREATE TABLE `dmigrations` (
             `id` int(11) NOT NULL auto_increment,
             `migration` VARCHAR(255) NOT NULL,
              PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        """
        _execute_in_transaction(create_new)
    
    def init(self):
        "Create the dmigration table, if necessary"
        if not self.migration_table_present():
            self.create_migration_table()
        from migration_log import init as log_init
        log_init()
    
    def resolve_name(self, name):
        """
        Resolve user-friendly migration name to real full migration name.
        So both "5" and "005_foo" become "005_foo.py" etc.
        
        Raises exception if ambiguous, returns None if not found.
        """
        name = str(name)
        if re.search('^\d+$', name):
            name = self.migration_db.find_unique_migration_by_number(
                int(name)
            )
        return name
    
    def force_resolve_name(self, name):
        """
        Resolve name or raise an exception if not possible.
        
        Raises exception if ambiguous or not found.
        """
        resolved_name = self.resolve_name(name)
        if resolved_name not in self.migration_db.list():
            raise NoSuchMigrationError(name)
        return resolved_name
    
    def list_considering_dev(self):
        """
        Return list of migrations considering value of dev flag.
        """
        return [
            m for m in self.migration_db.list() 
            if self.dev or not self.migration_db.is_dev_migration(m)
        ]
    
    def plan_to(self, point):
        """
        Point can be a migration name or a number.
        Number can resolve to an unique migration name,
        or to a point between migrations,
        but it cannot resolve to an ambiguous migration.
        
        Return plan to migrate to such point.
        """
        migrations = self.list_considering_dev()
        point = str(point)
        if point in migrations:
            i = migrations.index(point) + 1
        elif re.search(r'^\d+$', point):
            point = int(point)
            # NOTE: It only checks that the point is not a duplicate
            self.migration_db.find_unique_migration_by_number(point)
            i = 0
            while i < len(migrations) and \
                self.migration_db.migration_number(migrations[i]) <= point:
                i += 1
        else:
            raise NoSuchMigrationError(point)
        
        return _down(
            self.applied_only(reversed(migrations[i:]))
        ) + _up(
            self.unapplied_only(migrations[:i])
        )
    
    def applied_only(self, migrations):
        return [m for m in migrations if self.is_applied(m)]
    
    def unapplied_only(self, migrations):
        return [m for m in migrations if not self.is_applied(m)]
    
    def plan(self, action, *args):
        if action in ['all', 'up', 'down'] and len(args) > 0:
            raise Exception(u"Too many arguments")
        
        if action in ['upto', 'downto', 'to'] and len(args) != 1:
            raise Exception(u"Action %s requires exactly 1 argument" % action)
        
        if action == 'apply':
            return _up(self.unapplied_only(
                [self.force_resolve_name(arg) for arg in args]
            ))
        
        if action == 'unapply':
            return _down(self.applied_only(
                [self.force_resolve_name(arg) for arg in args]
            ))
        
        if action == 'all':
            return _up(self.unapplied_only(self.list_considering_dev()))
        
        if action == 'up':
            return _up(self.unapplied_only(self.list_considering_dev()))[:1]
        
        if action == 'down':
            return _down(reversed(
                self.applied_only(self.list_considering_dev())
            ))[:1]
        
        if action == 'to':
            return self.plan_to(*args)
        
        if action == 'downto':
            return [(m,a) for (m,a) in self.plan_to(*args) if a == 'down']
        
        if action == 'upto':
            return [(m,a) for (m,a) in self.plan_to(*args) if a == 'up']
        
        raise Exception(
            u"Unknown action %s" % " ".join([action] + list(args))
        )
