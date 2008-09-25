class NotMigrationSubclass:
    def __init__(self, sql_up, sql_down):
        pass

migration = NotMigrationSubclass(sql_up="", sql_down="")
