from datetime import datetime

from peewee import SqliteDatabase, Model, DateField, CharField, IntegerField

from src.main.python.manager.database_manager import DatabaseManager

db = SqliteDatabase('data.db')

class BaseModel(Model):
    class Meta:
        database = db

class ClientPetition(BaseModel):
    client_id = IntegerField(default=0)
    name_material = CharField(max_length=100)
    amount = IntegerField(default=0)
    digital_signature = CharField(max_length=100)
    order_date = DateField(default=datetime.now())

    def __str__(self):
        return f'{self.client_id} {self.name_material} {self.amount}'

    class Meta:
        db_table = 'client_petitions'
        order_by = ('order_date',)



if __name__ == '__main__':
    database_manager = DatabaseManager(db, [ClientPetition])
    database_manager.create_tables()
    ClientPetition.create(client_id=1, name_material='material1', amount=10, digital_signature='signature1')