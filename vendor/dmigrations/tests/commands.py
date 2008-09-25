from common import *
from django.core.management import call_command
import sys
from StringIO import StringIO

class CommandsTest(TestCase):
    def set_up(self):
        self.stdout = sys.stdout
    
    def tear_down(self):
        sys.stdout = self.stdout
    
    def test_that_syncdb_raises_exception_based_on_setting(self):
        from django.conf import settings
        old_setting = getattr(settings, 'DISABLE_SYNCDB', False)
        
        settings.DISABLE_SYNCDB = True
        self.assertRaises(SystemExit, call_command, 'syncdb')
        
        settings.DISABLE_SYNCDB = False
        self.assert_(not self.pipe_command('syncdb'))
        
        settings.DISABLE_SYNCDB = old_setting
    
    def pipe_command(self, *args, **kwargs):
        sys.stdout = StringIO()
        call_command(*args, **kwargs)
        res = sys.stdout.getvalue()
        sys.stdout = self.stdout
        return res
    
    def test_dmigration(self):
        from django.conf import settings
        if 'django.contrib.sessions' not in settings.INSTALLED_APPS:
            print "WARNING: Skipping ./manage.py dmigration tests, " \
                "add django.contrib.sessions to INSTALLED_APPS to run them"
            return
        
        # ./manage.py dmigration addcolumn sessions session session_key
        actual = self.pipe_command(
            'dmigration', "addcolumn", "sessions", "session", "session_key",
            output=True
        )
        expected = """from dmigrations.mysql import migrations as m\nimport datetime\nmigration = m.AddColumn('sessions', 'session', 'session_key', 'varchar(40) NOT NULL PRIMARY KEY')\n\n"""
        self.assert_equal(expected, actual)
        
        # ./manage.py dmigration migration new something
        actual = self.pipe_command(
            'dmigration', "new", "something", output=True
        )
        expected = """from dmigrations.mysql import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = []
        sql_down = []
        super(MyMigration, self).__init__(sql_up=sql_up, sql_down=sql_down)
    # Or override the up() and down() methods\n\nmigration = CustomMigration()\n\n"""
        self.assert_equal(expected, actual)
        
        # ./manage.py dmigration addindex sessions session expire_date
        actual = self.pipe_command(
            'dmigration', "addindex", "sessions", "session", "expire_date", 
            output=True
        )
        expected = """from dmigrations.mysql import migrations as m\nimport datetime\nmigration = m.AddIndex('sessions', 'session', 'expire_date')\n\n"""
        self.assert_equal(expected, actual)
        
        # Simply check they don't raise an exception
        actual = self.pipe_command(
            'dmigration', "app", "sessions", output=True
        )
        
        actual = self.pipe_command(
            'dmigration', "addtable", "sessions", "session", output=True
        )
        
        #actual = self.pipe_command(
        #    'dmigration', "insert", "sessions", "session", output=True
        #)
