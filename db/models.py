import datetime
from peewee import SqliteDatabase, Model, TextField, DateTimeField, PrimaryKeyField, CharField, \
    IntegerField, BooleanField, FloatField, ForeignKeyField

db = SqliteDatabase('/home/sergei/PycharmProjects/avito_bot/parser.db')


class BaseModel(Model):
    class Meta:
        database = db


class Category(BaseModel):
    category = CharField(unique=True)


class Type_transaction(BaseModel):
    type_transaction = CharField(unique=True)


class Location(BaseModel):
    location = CharField(unique=True)


class Property_type(BaseModel):
    property_type = CharField(unique=True)


class Parameter(BaseModel):
    property_type_id = ForeignKeyField(Property_type)
    security = BooleanField(null=True)
    property_area = IntegerField(null=True)


class Advertisement(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    id_avito = IntegerField(unique=True)
    url = CharField()
    name = CharField()
    description = TextField()
    category_id = ForeignKeyField(Category)
    type_transaction_id = ForeignKeyField(Type_transaction)
    location_id = ForeignKeyField(Location)
    time = DateTimeField()
    address = CharField()
    phone = BooleanField()
    delivery = BooleanField()
    message = BooleanField()
    parameter_id = ForeignKeyField(Parameter)
    coords_lat = FloatField()
    coords_lng = FloatField()
    date_creation = DateTimeField(default=datetime.datetime.now)
    date_update = DateTimeField(default=datetime.datetime.now)
    activated = BooleanField(default=True)

    class Meta:
        table_name = 'Advertisements'
        order_by = 'id'


class Image(BaseModel):
    image_url = CharField(null=False)
    advertisement_id = ForeignKeyField(Advertisement)


class Price(BaseModel):
    price = IntegerField()
    date_update = DateTimeField(default=datetime.datetime.now)
    advertisement_id = ForeignKeyField(Advertisement)


class User_tg(BaseModel):
    user_id = IntegerField(primary_key=True, unique=True)
    date_creation = DateTimeField(default=datetime.datetime.now)
    date_update = DateTimeField(default=datetime.datetime.now)
    activated = BooleanField(default=True)


class Filter(BaseModel):
    user_id = ForeignKeyField(User_tg)
    name_filter = CharField(unique=True)
    type_transaction_id = ForeignKeyField(Type_transaction)
    category_id = ForeignKeyField(Category)
    property_type_id = ForeignKeyField(Property_type, null=True)
    min_price = IntegerField(null=True)
    max_price = IntegerField(null=True)
    coords_lat = FloatField(null=True)
    coords_lng = FloatField(null=True)
    search_radius = IntegerField(null=True)
    parameter_property_area_min = IntegerField(null=True)
    parameter_property_area_max = IntegerField(null=True)
    profitability_rent = IntegerField(null=True)
    profitability_sale = IntegerField(null=True)
