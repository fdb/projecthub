class BaseMigration(object):
    def up(self):
        raise NotImplementedError
    
    def down(self):
        raise NotImplementedError
