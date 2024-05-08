class DatabaseManager:
    def __init__(self, db, models):
        self.db = db
        self.models = models

    def create_tables(self):
        self.db.connect()
        self.db.create_tables(self.models)
        self.db.close()

    def drop_tables(self):
        self.db.connect()
        self.db.drop_tables(self.models)
        self.db.close()
