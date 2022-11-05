import datetime

import peewee
from peewee import SqliteDatabase, Model, TextField, DateTimeField, PrimaryKeyField, CharField, \
    IntegerField, BooleanField, FloatField

db = SqliteDatabase('parser.db')


class BaseModel(Model):
    class Meta:
        database = db

class Advertisement(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    id_avito = IntegerField(unique=True)
    url = CharField()
    name = CharField()
    description = TextField()
    category = CharField() #разделить
    location = CharField() #разделить
    time = DateTimeField()
    price = IntegerField() #разделить
    images = TextField() #разделить
    address = CharField()
    phone = BooleanField()
    delivery = BooleanField()
    message = BooleanField()
    parameters = CharField()
    coords_lat = FloatField()
    coords_lng = FloatField()
    date_creation = DateTimeField(default=datetime.datetime.now)
    date_update = DateTimeField(default=datetime.datetime.now)
    activated = BooleanField(default=True)

    class Meta:
        table_name = 'Advertisements'
        order_by = 'id'

