class MigrationError(Exception):
    pass

class NoSuchMigrationError(MigrationError):
    def __init__(self, name):
        #super(Exception, self).__init__(u"No such migration: %s" % name)
        # NOTE: Trying to be 2.4 and 2.5 compatible
        self.message = u"No such migration: %s" % name
        self.args = [self.message]
        self.name = name

class BadMigrationError(MigrationError):
    pass

class AmbiguousMigrationNameError(MigrationError):
    pass

class InconsistentStateError(MigrationError):
    pass

class DevFlagRequiredError(MigrationError):
    pass
