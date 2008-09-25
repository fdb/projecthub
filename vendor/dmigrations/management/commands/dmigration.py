import re
import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection
from optparse import make_option
from django.conf import settings
from django.db import models

import pprint

class Command(BaseCommand):
    help = "Generate a new migration"
    option_list = BaseCommand.option_list + (
        make_option('--output', action='store_true', dest='output',
            help='Output migration to console instead of writing to file'),
    )
    requires_model_validation = True
    
    def handle(self, *args, **options):
        import_path = getattr(settings, 'DMIGRATION_GENERATOR',
            # Default generator depends on DATABASE_ENGINE
            'dmigrations.%s.generator' % settings.DATABASE_ENGINE
        )
        try:
            db_generator = __import__(import_path, {}, {}, [''])
        except ImportError, e:
            raise # Just let them see the error
        
        available_args = db_generator.get_commands()
        if args:
            arg, remaining = args[0], args[1:]
            if arg in available_args:
                available_args[arg](remaining, options.get('output'))
            else:
                # Print help and exit
                raise CommandError('Available options are %s' % ', '.join(
                    available_args.keys())
                )
        else:
            # Print instructions
            print "Use this tool to generate migrations"
            for arg, fn in available_args.items():
                print "  ./manage.py migration %s%s" % (arg, fn.__doc__)
            print "  Use the --output option to view a migration without " \
                "writing it to disk"

