import base64
import json
from datetime import datetime

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15
from peewee import SqliteDatabase, Model, DateField, CharField, IntegerField

db = SqliteDatabase('data.db')


class BaseModel(Model):

    @classmethod
    def create_new_table(cls):
        try:
            db.connect()
            db.create_tables([cls])
        finally:
            db.close()

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

    @staticmethod
    def from_json(json_string: str) -> 'ClientPetition':
        data = json.loads(json_string)
        return ClientPetition(data['client_id'], data['name_material'], data['amount'], data['digital_signature'],
                              data['order_date'])

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_dict(self) -> dict:
        return {
            'client_id': self.client_id,
            'name_material': self.name_material,
            'amount': self.amount,
            'digital_signature': self.digital_signature,
            'order_date': self.order_date
        }

    @staticmethod
    def from_jsons(json_string: str) -> 'ClientPetition':
        data = json.loads(json_string)
        for value in data:

            if 'client_id' in value:
                client_id, name_material, amount, digital_signature, order_date = ClientPetition._parse(value,
                                                                                                        'client_id',
                                                                                                        'name_material',
                                                                                                        'amount',
                                                                                                        'digital_signature',
                                                                                                        'order_date')

            else:
                client_id, name_material, amount, digital_signature, order_date = ClientPetition._parse(value,
                                                                                                        'clientId',
                                                                                                        'nameMaterial',
                                                                                                        'amount',
                                                                                                        'digitalSignature',
                                                                                                        'orderDate')

            ClientPetition.create(client_id=client_id, name_material=name_material, amount=amount,
                                  digital_signature=digital_signature, order_date=order_date)
            ClientPetition.create(client_id=1, name_material='material1', amount=10, digital_signature='signature1')

    @staticmethod
    def _parse(data, key_client_id, key_name_material, key_amount, key_digital_signature, key_order_date) -> None:
        client_id = data[key_client_id]
        if client_id.isdigit():
            client_id = int(client_id)
        else:
            raise ValueError("Invalid client_id")
        name_material = data[key_name_material]
        amount = data[key_amount]
        digital_signature = data[key_digital_signature]
        if not digital_signature.isalnum():
            raise ValueError("Invalid digital_signature")
        order_date = data[key_order_date]
        if not datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S'):
            raise ValueError("Invalid order_date")
        order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')

        # Verificar la firma digital
        public_key_path = 'ruta/al/archivo/de/clave/publica.pem'  # Reemplaza con la ruta de tu archivo de clave pública
        data_to_verify = json.dumps(data, sort_keys=True).encode(
            'utf-8')  # Convertir los datos a JSON y codificarlos en utf-8
        signature = base64.b64decode(digital_signature)  # Decodificar la firma digital de base64
        if not self.verify_signature(public_key_path, data_to_verify, signature):
            raise ValueError("Digital signature verification failed")

        return client_id, name_material, amount, digital_signature, order_date

    @staticmethod
    def verify_signature(public_key_path, data, signature):
        with open(public_key_path, "r") as key_file:
            public_key = RSA.import_key(key_file.read())
        verifier = pkcs1_15.new(public_key)
        digest = SHA256.new(data.encode('utf-8'))  # Codificar los datos antes de generar el hash
        signature_bytes = base64.b64decode(signature)  # Decodificar la firma desde base64
        return verifier.verify(digest, signature_bytes)


