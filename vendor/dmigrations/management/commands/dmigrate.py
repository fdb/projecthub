import os, sys
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.conf import settings
from StringIO import StringIO

from dmigrations.migration_state import MigrationState, table_present
from dmigrations.migration_db import MigrationDb
from dmigrations.exceptions import *

class Command(BaseCommand):
    help = """Commands:
./manage.py dmigrate apply M1 M1 - Apply specified migrations
./manage.py dmigrate unapply M1 M2 - Unapply specified migration
./manage.py dmigrate mark_as_applied M1 M2 - Mark specified migrations as applied without running them
./manage.py dmigrate mark_as_unapplied M1 M2 - Unapply specified migration as unapplied without running them
./manage.py dmigrate cat M1 M2 - Print specified migrations

./manage.py dmigrate all      - Run all migrations
./manage.py dmigrate up       - Apply oldest unapplied migration
./manage.py dmigrate down     - Unapply newest applied migration

./manage.py dmigrate to M     - Apply all migrations up to M, upapply all migrations newer than M
./manage.py dmigrate upto M   - Apply all migrations up to M
./manage.py dmigrate downto M - Upapply all migrations newer than M

./manage.py dmigrate init     - Ensure migration system is initialized

./manage.py dmigrate list     - List all migrations and their state
./manage.py dmigrate help     - Display this message
"""
    args = '[command] [arguments]'
    option_list = BaseCommand.option_list + (
        # NOTE: dev has three values, True, False, and None
        #       None works like False except when we're migrating
        #       from the old migration system and we need to know
        #       if DEV migrations were run or not.
        make_option('--dev', action='store_true', dest='dev',
            help='Run development migrations (DEV in the filename) as well'),
        make_option('--nodev', action='store_false', dest='dev',
            help='Exclude development migrations (DEV in the filename)'),
        make_option('--print-plan', action='store_true', dest='print_plan',
            help='Only print plan'),
        make_option('--verbosity', action='store', dest='verbosity',
            default='1', type='choice', choices=['0', '1', '2'],
            help='Verbosity level; 0=minimal, 1=normal output, 2=all output'),
    )
    requires_model_validation = False
    
    def handle(self, *args, **options):
        try:
            migrations_dir = settings.DMIGRATIONS_DIR
        except AttributeError:
            print "You need to add DMIGRATIONS_DIR to your settings"
            return
        migration_db = MigrationDb(directory = migrations_dir)
        migration_state = MigrationState(
            migration_db = migration_db, dev = options.get('dev')
        )
        verbosity = int(options.get('verbosity', 1))
        
        if not args or args[0] == 'help':
            # TODO: Do this without calling os.system
            os.system('./manage.py help dmigrate')
            return
        
        elif args[0] in 'all up down upto downto to apply unapply'.split():
            migration_state.init()
            for (migration_name, action) in migration_state.plan(*args):
                migration = migration_db.load_migration_object(migration_name)
                if action == 'up':
                    if verbosity >= 1:
                        print "Applying migration %s" % migration.name
                    if not options.get('print_plan'):
                        migration_state.apply(migration_name)
                else:
                    if verbosity >= 1:
                        print "Unapplying migration %s" % migration.name
                    if not options.get('print_plan'):
                        migration_state.unapply(migration_name)
        
        elif args[0] == 'mark_as_applied':
            migration_state.init()
            for name in args[1:]:
                resolved_name = migration_state.resolve_name(name)
                if resolved_name == None:
                    raise NoSuchMigrationError(name)
                migration_state.mark_as_applied(resolved_name)
        
        elif args[0] == 'mark_as_unapplied':
            migration_state.init()
            for name in args[1:]:
                resolved_name = migration_state.resolve_name(name)
                if resolved_name == None:
                    raise NoSuchMigrationError(name)
                migration_state.mark_as_unapplied(resolved_name)
        
        elif args[0] == 'list':
            migration_state.init()
            for migration_name in migration_db.list():
                if migration_state.is_applied(migration_name):
                   print "* [+] %s" % migration_name
                else:
                   print "* [ ] %s" % migration_name
            migrations_not_in_db = migration_state.applied_but_not_in_db()
            if migrations_not_in_db:
                print "These migrations are marked as applied but cannot " \
                    "be found:"
                for migration_name in migrations_not_in_db:
                    print "* [?] %s" % migration_name
            return
        
        elif args[0] == 'init':
            migration_state.init()
        
        elif args[0] == 'cat':
            for name in args[1:]:
                print open(
                    migration_db.resolve_migration_path(name), 'r'
                ).read()
            return
        
        else:
            raise CommandError(
                'Argument should be one of: list, help, up, down, all, init, '
                'apply, unapply, to, downto, upto, mark_as_applied, '
                'mark_as_unapplied'
            )
        
        # Ensure Django permissions and content_types have been created
        # NOTE: Don't run if django_content_type doesn't exist yet.
        if table_present('django_content_type'):
            from django.contrib.auth.management import create_permissions
            from django.db import models
            for app in models.get_apps():
                if verbosity >= 1:
                    create_permissions(app, set(), 2)
                else:
                    create_permissions(app, set(), 1)
