"""
Functions that code-generate migrations, used by the ./manage.py dmigration
command.
"""
from django.core.management.base import CommandError
from django.core.management.color import no_style
from django.db import connection
from django.db import models
from django.conf import settings
from dmigrations.generator_utils import save_migration

import re

def get_commands():
    return {
        'app': add_app,
        'addindex': add_index,
        'addcolumn': add_column,
        'addtable': add_table,
        'new': add_new,
        'insert': add_insert,
    }

def add_app(args, output):
    " <app>: Add tables for a new application"
    if len(args) != 1:
        raise CommandError('./manage.py migration app <name-of-app>')
    app_label = args[0]
    app = models.get_app(app_label)
    from django.core.management.sql import sql_create
    
    up_sql = sql_create(app, no_style())
    down_sql = sql_delete(app, no_style())
    
    app_name = app.__name__.replace('.', '_')
    migration_output = app_mtemplate % (
        clean_up_create_sql(up_sql), clean_up_create_sql(down_sql)
    )
    migration_output = migration_code(migration_output)
    
    save_migration(output, migration_output, app_name)

def add_table(args, output):
    " <app> <model>: Add tables for a new model"
    if len(args) != 2:
        raise CommandError('./manage.py migration app <name-of-app>')
    app_label, model = args
    app = models.get_app(app_label)
    app_name = app.__name__.replace('.', '_')
    model_to_add = models.get_model(app_label, model)
    
    if not model_to_add:
        raise Exception("Model %s in app %s not found" % (model, app_label))
    
    # The following code is a bit of a mess. I copied it from 
    # django.core.management.sql.sql_create without a full understanding of 
    # how it all works. Ideally this needs to refactored in Django itself to 
    # make it easier for libraries such as this one to reuse the table 
    # creation logic.
    style = no_style()
    app_models = models.get_models(app)
    up_sql = []
    tables = connection.introspection.table_names()
    known_models = set([
        model for model in connection.introspection.installed_models(tables)
        if model not in app_models]
    )
    pending_references = {}

    sql_output, references = connection.creation.sql_create_model(
        model_to_add, style, known_models
    )
    up_sql.extend(sql_output)
    for refto, refs in references.items():
        pending_references.setdefault(refto, []).extend(refs)
        if refto in known_models:
            up_sql.extend(
                connection.creation.sql_for_pending_references(
                    refto, style, pending_references
                )
            )
    up_sql.extend(
        connection.creation.sql_for_pending_references(
            model, style, pending_references
        )
    )
    # Keep track of the fact that we've created the table for this model.
    known_models.add(model_to_add)

    # Create the many-to-many join tables.
    up_sql.extend(
        connection.creation.sql_for_many_to_many(model_to_add, style)
    )
    if not up_sql:
        raise Exception("Model %s in app %s not found" % (model, app_label))
    
    # Down sql just drops any tables we have created
    down_sql = []
    for sql in up_sql:
        if sql.startswith('CREATE TABLE'):
            down_sql.append('DROP TABLE %s;' % sql.split()[2])
    
    # Reverse the order of down_sql
    down_sql = down_sql[::-1]
    
    migration_output = app_mtemplate % (
        clean_up_create_sql(up_sql), clean_up_create_sql(down_sql)
    )
    migration_output = migration_code(migration_output)
    
    save_migration(output, migration_output, app_name)

def add_index(args, output):
    " <app> <model> <column>: Add an index"
    if len(args) != 3:
        raise CommandError(
            './manage.py migration addindex <app> <model> <column>'
        )
    app_label, model, column = args
    
    migration_output = add_index_mtemplate % (app_label, model, column)
    migration_output = migration_code(migration_output)
    save_migration(output, migration_output, 'add_index_%s_%s_%s' % (
        app_label, model, column
    ))

def add_column(args, output):
    " <app> <model> <column> [<column2> ...]: Add one or more columns"
    if len(args) < 3:
        raise CommandError(
            './manage.py migration addcolumn <app> <model> <column> '
            '[<column2> ...]'
        )
    
    app_label, model, columns = args[0], args[1], args[2:]
    actual_model = models.get_model(app_label, model)
    
    style = no_style()
    sql, references = connection.creation.sql_create_model(
        actual_model, style, set()
    )
    
    col_specs = []
    for column in columns:
        is_foreign_key = isinstance(
            actual_model._meta.get_field_by_name(column)[0], models.ForeignKey
        )
        col_specs.append((
            column,
            extract_column_spec(sql[0], column, is_foreign_key),
            is_foreign_key
        ))
         
    migration_defs = [
        add_column_mtemplate % (app_label, model, column, col_spec)
        for (column, col_spec, is_foreign_key) in col_specs 
        if not is_foreign_key
    ]
    migration_fk_defs = [
      add_column_foreignkey_mtemplate % (
        app_label, model, column, col_spec,
        actual_model._meta.get_field_by_name(column)[0].rel.to._meta.db_table
      )
      for (column, col_spec, is_foreign_key) in col_specs 
      if is_foreign_key
    ]
    if migration_fk_defs:
        print >>sys.stderr, """Warning!
You have added columns that are foreign keys (%s).
These will be added as nullable. If you need them to be NOT NULL, then you
have to write another migration to do that, after you've populated them
with data.""" % ','.join([column for (column, x, fk) in col_specs if fk])
    
    migration_defs += migration_fk_defs
    migration_output = migration_code(*migration_defs)
    
    if len(columns) == 1:
        migration_name = 'add_column_%s_to_%s_%s' % (
            columns[0], app_label, model
        )
    else:
        migration_name = 'add_columns_%s_to_%s_%s' % (
            "_and_".join(columns), app_label, model
        )
    
    save_migration(output, migration_output, migration_name)

def add_new(args, output):
    " <description>: Create empty migration (uses description in filename)"
    if not args:
        raise CommandError('./manage.py migration new <description>')
    
    db_engine = getattr(settings, 'DMIGRATIONS_DATABASE_BACKEND', 'mysql')
    
    save_migration(
        output, skeleton_template % db_engine, '_'.join(args).lower()
    )

def add_insert(args, output):
    " <app> <model>: Create insert migration for data in table"
    if len(args) != 2:
        raise CommandError('./manage.py migration insert <app> <model>')
    
    app_label, model = args
    table_name = '%s_%s' % (app_label, model)
    
    def get_columns(table_name):
        "Returns columns for table"
        cursor = connection.cursor()
        cursor.execute('describe %s' % table_name)
        rows = cursor.fetchall()
        cursor.close()

        # Sanity check that first column is called 'id' and is primary key
        first = rows[0]
        assert first[0] == u'id', 'First column must be id'
        assert first[3] == u'PRI', 'First column must be primary key'

        return [r[0] for r in rows]

    def get_dump(table_name):
        "Returns {'table_name':..., 'columns':..., 'rows':...}"
        columns = get_columns(table_name)
        # Escape column names with `backticks` - so columns with names that
        # match MySQL reserved words (e.g. "order") don't break things
        escaped_columns = ['`%s`' % column for column in columns]
        sql = 'SELECT %s FROM %s' % (', '.join(escaped_columns), table_name)

        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()

        return {
            'table_name': table_name,
            'columns': columns,
            'rows': rows,
        }
    
    dump = get_dump(table_name)
    
    migration_output = insert_mtemplate % {
        'table_name': dump['table_name'],
        'columns': repr(dump['columns']),
        'insert_rows': pprint.pformat(dump['rows']),
        'delete_ids': ', '.join(map(str, [r[0] for r in dump['rows']])),
    }
    migration_output = migration_code(migration_output)
    
    save_migration(output, migration_output, 'insert_into_%s_%s' % (
        app_label, model
    ))

def sql_delete(app, style):
    "Returns a list of the DROP TABLE SQL statements for the given app."
    # This is a modified version of the function in django.core.management.sql
    # - the original only emits drop table statements for tables that 
    # currently exist in the database, but we want them all regardless
    from django.db import connection, models
    from django.db.backends.util import truncate_name
    from django.contrib.contenttypes import generic
    
    table_names = []
    output = []
    
    # Output DROP TABLE statements for standard application tables.
    to_delete = set()
    
    references_to_delete = {}
    app_models = models.get_models(app)
    for model in app_models:
        opts = model._meta
        for f in opts.local_fields:
            if f.rel and f.rel.to not in to_delete:
                references_to_delete.setdefault(f.rel.to, []).append(
                    (model, f)
                )
        
        to_delete.add(model)
    
    for model in app_models:
        output.extend(
            connection.creation.sql_destroy_model(
                model, references_to_delete, style
            )
        )
    
    # Output DROP TABLE statements for many-to-many tables.
    for model in app_models:
        opts = model._meta
        for f in opts.local_many_to_many:
            output.extend(
                connection.creation.sql_destroy_many_to_many(model, f, style)
            )
    
    return output[::-1] # Reverse it, to deal with table dependencies.


def clean_up_create_sql(sqls):
    "Ensures create table uses correct engine, cleans up whitespace"
    
    engine = getattr(settings, 'DMIGRATIONS_MYSQL_ENGINE', 'InnoDB')
    
    def neat_format(sql):
        def indent4(s):
            lines = s.split('\n')
            return '\n'.join(['    %s' % line for line in lines])
        
        bits = ['"""\n%s\n"""' % indent4(bit) for bit in sql]
        return '[%s]' % ', '.join(bits)
    
    def fix_create_table(sql):
        if sql.strip().startswith("CREATE TABLE"):
            # Find the last ')'
            last_index = sql.rindex(')')
            tail = sql[last_index:]
            if 'InnoDB' not in tail:
                tail = tail.replace(
                    ')', ') ENGINE=%s DEFAULT CHARSET=utf8' % engine
                )
            sql = sql[:last_index] + tail
        return sql
    
    return neat_format(map(fix_create_table, sqls))

def extract_column_spec(sql, column, is_foreign_key=False):
    "Extract column creation spec from a CREATE TABLE statement"
    lines = sql.split('\n')
    escaped_column = '`%s`' % column
    if is_foreign_key: escaped_column = '`%s_id`' % column
    for line in lines:
        line = line.strip()
        if line.startswith(escaped_column):
            line = line.replace(escaped_column, '')
            line = line.rstrip(',') # Remove trailing comma
            return line.strip()
    assert False, 'Could not find column spec for column %s' % column


migration_template = """from dmigrations.%(db_engine)s import migrations as m
import datetime
migration = %(migration_body)s
"""

def migration_code(*migration_defs):
    db_engine = getattr(settings, 'DMIGRATIONS_DATABASE_BACKEND', 'mysql')
    if len(migration_defs) == 1:
        migration_body = migration_defs[0]
    else:
        migration_body = (
            "m.Compound([\n" + 
            "".join([
                "    %s,\n" % m for m in migration_defs
            ]) + 
            "])\n"
        )
    
    return migration_template % {
        'db_engine': db_engine,
        'migration_body': migration_body
    }

# Templates for code generation
add_column_mtemplate = "m.AddColumn('%s', '%s', '%s', '%s')"
add_column_foreignkey_mtemplate = "m.AddColumn('%s', '%s', '%s', '%s', '%s')"

add_index_mtemplate = "m.AddIndex('%s', '%s', '%s')"

app_mtemplate = "m.Migration(sql_up=%s, sql_down=%s)"

insert_mtemplate = """m.InsertRows(
    table_name = '%(table_name)s',
    columns = %(columns)s,
    insert_rows = %(insert_rows)s,
    delete_ids = [%(delete_ids)s]
)"""

skeleton_template = """from dmigrations.%s import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = []
        sql_down = []
        super(CustomMigration, self).__init__(
            sql_up=sql_up, sql_down=sql_down
        )
    # Or override the up() and down() methods

migration = CustomMigration()
"""
