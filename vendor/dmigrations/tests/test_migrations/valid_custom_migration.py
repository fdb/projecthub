from dmigrations.mysql.migrations import Migration

class MyCrazyMigration(Migration):
    pass

migration = MyCrazyMigration(sql_up="", sql_down="")
