"""
These classes represent possible migrations. A migration is simply an object
with an up() method and a down() method - the down() method is allowed to 
raise an IrreversibleMigration exception. These objects are instances of 
subclasses of BaseMigration. Migration classes will be provided for stuff 
ranging from basic SQL migrations to more specialised things such as adding 
or removing an index.
"""
from dmigrations.migrations import BaseMigration
import re

class IrreversibleMigrationError(Exception):
    pass

class Migration(BaseMigration):
    "Explict SQL migration, with sql for migrating both up and down"
    
    def __init__(self, sql_up, sql_down=None):
        self.sql_up = sql_up
        self.sql_down = sql_down
    
    def up(self):
        self.execute_sql(self.sql_up)
    
    def down(self):
        if self.sql_down:
            self.execute_sql(self.sql_down)
        else:
            raise IrreversibleMigrationError, 'No sql_down provided'
    
    def execute_sql(self, sql, return_rows=False):
        "Executes sql, which can be a string or a list of strings"        
        statements = []
        if isinstance(sql, basestring):
            # Split string in to multiple statements
            statements_re = re.compile(r";[ \t]*$", re.M)
            statements = [s for s in statements_re.split(sql) if s.strip()]
        elif isinstance(sql, (list, tuple)):
            # Assume each item in the list is already an individual statement
            statements = sql
        else:
            assert False, 'sql argument must be string or list/tuple'
        
        from django.db import connection
        cursor = connection.cursor()
        
        for statement in statements:
            # Escape % due to format strings
            cursor.execute(statement.replace('%', '%%'))
        
        if return_rows:
            return cursor.fetchall()
    
    def __str__(self):
        return 'Migration, up: %r, down: %r' % (self.sql_up, self.sql_down)
    
class Compound(BaseMigration):
    """
    A migration that is composed of one or more other migrations. DO NOT USE.
    """
    def __init__(self, migrations=[]):
        self.migrations = migrations
    
    def up(self):
        for migration in self.migrations:
            migration.up()
    
    def down(self):
        for migration in reversed(self.migrations):
            migration.down()

    def __str__(self):
        return 'Compound Migration: %s' % self.migrations


class AddColumn(Migration):
    "A migration that adds a database column"
    
    add_column_sql = 'ALTER TABLE `%s_%s` ADD COLUMN `%s` %s;'
    drop_column_sql = 'ALTER TABLE `%s_%s` DROP COLUMN `%s`;'
    constrain_to_table_sql = 'ALTER TABLE `%s_%s` ADD CONSTRAINT %s FOREIGN KEY (`%s`) REFERENCES `%s` (`id`);'
    constrain_to_table_down_sql = 'ALTER TABLE `%s_%s` DROP FOREIGN KEY `%s`;'
    
    def __init__(self, app, model, column, spec, constrain_to_table=None):
        self.app, self.model, self.column, self.spec = app, model, column, spec
        if constrain_to_table:
            # this can only be used for ForeignKeys that link to another table's
            # id field. It is not for arbitrary relationships across tables!
            # Note also that this will create the ForeignKey field as allowing
            # nulls. Even if you don't want it to. This is because if it doesn't
            # allow null then the migration will blow up, because we're adding
            # the column without adding data to it. So you have to write another
            # migration later to change it from NULL to NOT NULL if you need to,
            # after you've populated it.
            
            # add the FK constraint
            constraint_name = "%s_refs_id_%x" % (column, abs(hash((model,constrain_to_table))))
            sql_up = [self.constrain_to_table_sql % (app, model, constraint_name, "%s_id" % column, constrain_to_table)]
            
            sql_up.insert(0,self.add_column_sql % (app, model, "%s_id" % column, spec))
            sql_down = [self.drop_column_sql % (app, model, "%s_id" % column)]
            # if add_column_sql has NOT NULL in it, bin it
            sql_up[0] = sql_up[0].replace(" NOT NULL", "")
            # drop FK on sql_down
            sql_down.insert(0,self.constrain_to_table_down_sql % (app, model, constraint_name))
            
        else:
            sql_up = [self.add_column_sql % (app, model, column, spec)]
            sql_down = [self.drop_column_sql % (app, model, column)]
            
        super(AddColumn, self).__init__(
            sql_up,
            sql_down,
        )
    
    def __str__(self):
        return "AddColumn: app: %s, model: %s, column: %s, spec: %s" % (
            self.app, self.model, self.column, self.spec
        )

class DropColumn(AddColumn):
    """
    A migration that drops a database column. Needs the full column spec so 
    it can correctly create the down() method.
    """
    def __init__(self, *args, **kwargs):
        super(DropColumn, self).__init__(*args, **kwargs)
        # Now swap over the sql_up and sql_down properties
        self.sql_up, self.sql_down = self.sql_down, self.sql_up

    def __str__(self):
        return super(DropColumn, self).replace('AddColumn', 'DropColumn')

class AddIndex(Migration):
    "A migration that adds an index (and removes it on down())"
    
    add_index_sql = 'CREATE INDEX `%s` ON `%s_%s` (`%s`);'
    drop_index_sql = 'ALTER TABLE %s_%s DROP INDEX `%s`;'
    
    def __init__(self, app, model, column):
        self.app, self.model, self.column = app, model, column
        index_name = '%s_%s_%s' % (app, model, column)
        super(AddIndex, self).__init__(
            sql_up = [self.add_index_sql % (index_name, app, model, column)],
            sql_down = [self.drop_index_sql % (app, model, index_name)],
        )
    
    def __str__(self):
        return "AddIndex: app: %s, model: %s, column: %s" % (
            self.app, self.model, self.column
        )

class DropIndex(AddIndex):
    "Drops an index"
    def __init__(self, app, model, column):
        super(DropIndex, self).__init__(app, model, column)
        self.sql_up, self.sql_down = self.sql_down, self.sql_up
    
    def __str__(self):
        return super(DropIndex, self).replace('AddIndex', 'DropIndex')

class InsertRows(Migration):
    "Inserts some rows in to a table"
    
    insert_row_sql = 'INSERT INTO `%s` (%s) VALUES (%s)'
    delete_rows_sql = 'DELETE FROM `%s` WHERE id IN (%s)'
    
    def __init__(self, table_name, columns, insert_rows, delete_ids):
        self.table_name = table_name
        sql_up = []
        from django.db import connection # so we can use escape_string
        connection.cursor() # Opens connection if not already open
        
        def escape(v):
            if v is None:
                return 'null'
            v = unicode(v) # In case v is an integer or long
            # escape_string wants a bytestring
            escaped = connection.connection.escape_string(v.encode('utf8'))
            # We get bugs if we use bytestrings elsewhere, so convert back to unicode
            # http://sourceforge.net/forum/forum.php?thread_id=1609278&forum_id=70461
            return u"'%s'" % escaped.decode('utf8')
        
        for row in insert_rows:
            values = ', '.join(map(escape, row))
            sql_up.append(
                self.insert_row_sql % (
                    table_name, ', '.join(map(str, columns)), values
                )
            )
        
        if delete_ids:
            sql_down = [self.delete_rows_sql % (table_name, ', '.join(map(str, delete_ids)))]
        else:
            sql_down = ["SELECT 1"]
        
        super(InsertRows, self).__init__(
            sql_up = ["BEGIN"] + sql_up + ["COMMIT"],
            sql_down = ["BEGIN"] + sql_down + ["COMMIT"],
        )
