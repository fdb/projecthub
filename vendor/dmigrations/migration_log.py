import datetime
from migration_state import _execute, _execute_in_transaction, table_present

MIGRATION_LOG_SQL = """
    CREATE TABLE `dmigrations_log` (
    `id` int(11) NOT NULL auto_increment,
    `action` VARCHAR(255) NOT NULL,
    `migration` VARCHAR(255) NOT NULL,
    `status` VARCHAR(255) NOT NULL,
    `datetime` DATETIME NOT NULL,
     PRIMARY KEY  (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8
"""

def init():
    """
    Create migration log if it doesn't exist
    """
    if not table_present('dmigrations_log'):
      _execute(MIGRATION_LOG_SQL)
  
def get_log():
    return list(_execute("""
        SELECT action, migration, status, datetime 
        FROM dmigrations_log 
        ORDER BY datetime, id"""
    ).fetchall())

def log_action(action, migration, status, when=None):
    if when == None:
        when = datetime.datetime.now()
    _execute_in_transaction("""
        INSERT INTO dmigrations_log(action, migration, status, datetime) 
        VALUES (%s, %s, %s, %s)
    """, [action, migration, status, when])
