import base64
import json
from datetime import datetime

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15
from loguru import logger
from peewee import SqliteDatabase, Model, DateField, CharField, IntegerField, TimeField, DateTimeField
import traceback


db = SqliteDatabase('data.db')


class BaseModel(Model):

    @classmethod
    def create_new_table(cls):
        try:
            db.connect()
            db.create_tables([cls])
        finally:
            db.close()

    @classmethod
    def drop_old_table(cls):
        db.connect()
        db.drop_tables([cls])
        db.close()

    class Meta:
        database = db


class ClientPetition(BaseModel):
    client_id = IntegerField(default=0)
    name_material = CharField(max_length=100)
    amount = IntegerField(default=0)
    order_date = DateTimeField(formats=['%Y-%m-%d %H:%M:%S'])

    def __str__(self):
        return f'{self.client_id} {self.name_material} {self.amount}'

    class Meta:
        db_table = 'client_petitions'
        order_by = ('order_date',)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_dict(self) -> dict:
        return {
            'client_id': self.client_id,
            'name_material': self.name_material,
            'amount': self.amount,
            'order_date': self.order_date,
        }

    @staticmethod
    def from_jsons(json_string: str) -> 'ClientPetition':
        data = json.loads(json_string)
        for value in data:

            if 'client_id' in value:
                client_id, name_material, amount, order_date = ClientPetition._parse(value,
                                                                                                        'client_id',
                                                                                                        'name_material',
                                                                                                        'amount',
                                                                                                        'digital_signature',
                                                                                                        'order_date',
                                                                                     'public_key')

            else:
                client_id, name_material, amount, digital_signature, order_date = ClientPetition._parse(value,
                                                                                                        'clientId',
                                                                                                        'nameMaterial',
                                                                                                        'amount',
                                                                                                        'digitalSignature',
                                                                                                        'orderDate',
                                                                                                        'publicKey')

            ClientPetition.create(client_id=client_id, name_material=name_material, amount=amount,
                                  order_date=order_date)
            logger.success(f"Digital Sign verified and Delivery Petition has been saved succesfully.")

    @staticmethod
    def _parse(data, key_client_id, key_name_material, key_amount, key_digital_signature, key_order_date, key_public_key) -> None:
        client_id = data[key_client_id]
        pk = data[key_public_key]
        if client_id.isdigit():
            client_id = int(client_id)
        else:
            raise ValueError("Invalid client_id")
        name_material = data[key_name_material]
        amount = data[key_amount]
        if amount < 0 or amount > 301:
            raise ValueError("Invalid amount")
        digital_signature = data[key_digital_signature]
        order_date = data[key_order_date]
        if not datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S'):
            raise ValueError("Invalid order_date")
        order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')

        # Verificar la firma digital
        signature = base64.b64decode(digital_signature)  # Decodificar la firma digital de base64
        if not ClientPetition.verify_signature(pk, order_date, signature):
            raise ValueError("Digital signature verification failed")

        return client_id, name_material, amount, digital_signature, order_date

    @staticmethod
    def verify_signature(public_key, order_date, signature):
        # Importar la clave pública
        public_key = RSA.import_key(ClientPetition.convert_to_pem(public_key))

        # Crear un objeto verificador de firma
        verifier = pkcs1_15.new(public_key)

        # Convertir la fecha de pedido a una cadena de caracteres y luego codificarla en UTF-8
        order_date_str = order_date.strftime("%Y-%m-%d %H:%M:%S")
        order_date_bytes = order_date_str.encode('utf-8')

        # Calcular el hash de los datos
        digest = SHA256.new(order_date_bytes)

        # Verificar la firma
        try:
            verifier.verify(digest, signature)
            print("Verified signature")
            return True  # La firma es válida
        except ValueError:
            return False  # La firma no es válida

    import base64

    @staticmethod
    def convert_to_pem(public_key_base64):
        public_key_pem = "-----BEGIN PUBLIC KEY-----\n" + public_key_base64 + "\n-----END PUBLIC KEY-----"
        return public_key_pem


if __name__ == "__main__":
    # Generar un par de claves
    key_pair = RSA.generate(2048)

    # Datos originales
    original_data = "Hello, World!"

    # Firmar los datos
    signature = pkcs1_15.new(key_pair).sign(SHA256.new(original_data.encode('utf-8')))

    # Verificar la firma
    verifier = pkcs1_15.new(key_pair.publickey())
    try:
        verifier.verify(SHA256.new(original_data.encode('utf-8')), signature)
        print("La firma digital es válida.")
    except (ValueError, TypeError):
        print("La firma digital no es válida.")


