from django.core.management.commands.syncdb import Command as Original
import sys

class Command(Original):
    """
    Our own version of syncdb that obeys the DISABLE_SYNCDB setting.
    """
    def handle_noargs(self, **options):
        from django.conf import settings
        if getattr(settings, 'DISABLE_SYNCDB', False):
            sys.stderr.write(
                'Use dmigrations, not syncdb - "%s help dmigrate" for help\n' 
                % sys.argv[0]
            )
            sys.exit(1)
        else:
            super(Command, self).handle_noargs(**options)
