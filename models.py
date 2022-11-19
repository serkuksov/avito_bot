import datetime
import logging

from avito_parser import Advertisement as Ad_avito
from peewee import SqliteDatabase, Model, TextField, DateTimeField, PrimaryKeyField, CharField, \
    IntegerField, BooleanField, FloatField, ForeignKeyField

db = SqliteDatabase('parser.db')


class BaseModel(Model):
    class Meta:
        database = db


class Category(BaseModel):
    category = CharField(null=False)
    transaction = CharField(null=False)


class Location(BaseModel):
    location = CharField(unique=True, null=False)


class Advertisement(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    id_avito = IntegerField(unique=True)
    url = CharField()
    name = CharField()
    description = TextField()
    category_id = ForeignKeyField(Category)  # разделить
    location_id = ForeignKeyField(Location)  # разделить
    time = DateTimeField()
    # price = IntegerField()  # разделить
    # images = TextField()  # разделить
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


class Image(BaseModel):
    image_url = CharField(null=False)
    advertisement_id = ForeignKeyField(Advertisement)


class Price(BaseModel):
    price = IntegerField(null=False)
    date_update = DateTimeField(default=datetime.datetime.now)
    advertisement_id = ForeignKeyField(Advertisement)


def create_advertisement(advertisement: Ad_avito):
    """Добавляет новое объявление"""
    ad = Advertisement(
        id_avito=advertisement.id_avito,
        url=advertisement.url,
        name=advertisement.name,
        description=advertisement.description,
        category_id=get_category_id(advertisement.category),
        location_id=get_location_id(advertisement.location),
        time=advertisement.time,
        address=advertisement.address,
        phone=advertisement.phone,
        delivery=advertisement.delivery,
        message=advertisement.message,
        parameters=advertisement.parameters,
        coords_lat=advertisement.coords_lat,
        coords_lng=advertisement.coords_lng
    )
    ad.save()
    Price.create(price=advertisement.price, advertisement_id=ad)
    for image in advertisement.images:
        Image.create(image_url=image, advertisement_id=ad)
    message = f'Добавлено новое объявление {advertisement.url} с ценой {advertisement.price}'
    logging.info(message)
    return message


def get_category_id(category: str, transaction: str = 'Купить') -> int:
    """Получить id категорри, если нет создать новую категорию и вернуть id"""
    try:
        category_id = Category.get((Category.category == category) & (Category.transaction == transaction))
    except:
        category_id = Category.create(category=category, transaction=transaction).id
    return category_id


def get_location_id(location: str) -> int:
    """Получить id локации, если нет создать новую категорию и вернуть id"""
    try:
        location_id = Location.select(Location.location == location)
    except:
        location_id = Location.create(category=location).id
    return location_id


def set_modification_price(price: int, date: datetime, advertisement: Advertisement) -> str:
    """Добавить новую цену объявления если она изменилась.
    Возвращает сообщение об успехе"""
    old_price = Price.select().where(Price.advertisement_id == advertisement.id).order_by(
        Price.date_update.desc()).get().price
    if old_price != price:
        Price.create(price=price, date_update=date, advertisement_id=advertisement.id)
        message = f'Изменение цены для {advertisement.url} c {old_price} до {price}'
        logging.info(message)
        return message


def set_advertisement(advertisement: Ad_avito) -> str:
    """Производит активацию, изменение цены и добавление (если его нет) объявления в базу"""
    ad = Advertisement.select().where(Advertisement.id_avito == advertisement.id_avito)
    if ad.exists():
        ad = ad.get()
        date = datetime.datetime.now()
        message = set_modification_price(price=advertisement.price, date=date, advertisement=ad)
        ad.date_update = datetime.datetime.now()
        if not ad.activated:
            ad.activated = True
            logging.info(f'Объявление {ad.url} активировано')
        ad.save()
    else:
        message = create_advertisement(advertisement=advertisement)
    return message


def deactivation_advertisement():
    """Активирует ранее снятое объявление"""
    date_update = datetime.datetime.now() - datetime.timedelta(hours=1)
    deactivation_list = Advertisement.select(). \
        where((Advertisement.date_update < date_update) & Advertisement.activated)
    for elm in deactivation_list:
        logging.info(f'Объявление {elm.url} снято')
        elm.activated = False
        elm.save()



