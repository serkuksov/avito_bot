import datetime
import logging
import statistics
import re

from avito_parser import Advertisement as Ad_avito
from peewee import SqliteDatabase, Model, TextField, DateTimeField, PrimaryKeyField, CharField, \
    IntegerField, BooleanField, FloatField, ForeignKeyField, Expression

db = SqliteDatabase('parser.db')


class BaseModel(Model):
    class Meta:
        database = db


class Category(BaseModel):
    category = CharField(null=False)
    transaction = CharField(null=False)


class Location(BaseModel):
    location = CharField(unique=True)


class Property_type(BaseModel):
    property_type = CharField(unique=True)


class Parameter(BaseModel):
    property_type_id = ForeignKeyField(Property_type)
    security = BooleanField()
    property_area = IntegerField(null=True)


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


def get_property_area(name: str) -> int:
    property_area = re.findall(r'\d+', name)
    if property_area:
        return int(property_area[0])
def get_parameters_in_dict(parameters: str) -> dict:
    dict_params = {}
    params = parameters.split(', ')
    dict_params['property_type'] = params[0]
    if len(params) > 1:
        security = True
    else:
        security = False
    dict_params['security'] = security
    return dict_params


def create_parameter(advertisement: Ad_avito):
    """Добавляет параметры нового объявления"""
    dict_params = get_parameters_in_dict(advertisement.parameters)
    property_area = get_property_area(advertisement.name)
    property_type_id = get_property_type_id(dict_params['property_type'])
    security = dict_params['security']
    parameter_id = Parameter.create(property_type_id=property_type_id, property_area=property_area, security=security)
    return parameter_id


def create_advertisement(advertisement: Ad_avito):
    """Добавляет новое объявление"""
    ad = Advertisement(
        id_avito=advertisement.id_avito,
        url=advertisement.url,
        name=advertisement.name,
        description=advertisement.description,
        category_id=get_category_id(category=advertisement.category),
        location_id=get_location_id(location=advertisement.location),
        time=advertisement.time,
        address=advertisement.address,
        phone=advertisement.phone,
        delivery=advertisement.delivery,
        message=advertisement.message,
        parameter_id=create_parameter(advertisement=advertisement),
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
        location_id = Location.get(Location.location == location)
    except:
        location_id = Location.create(location=location).id
    return location_id


def get_property_type_id(property_type: str) -> int:
    """Получить id типа недвижимости, если нет создать новый тип и вернуть id"""
    try:
        property_type_id = Property_type.get(Property_type.property_type == property_type)
    except:
        property_type_id = Property_type.create(property_type=property_type).id
    return property_type_id


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
    """Производит изменение цены и добавление (если его нет) объявления в базу"""
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


def get_search_term_by_distance(coords_lat: float, coords_lng: float, search_radius: int) -> Expression:
    expression_for_distance = ((coords_lat - Advertisement.coords_lat) * (coords_lat - Advertisement.coords_lat) +
                (coords_lng - Advertisement.coords_lng) * (coords_lng - Advertisement.coords_lng)) \
               * 111000 * 111000 <= search_radius * search_radius
    return expression_for_distance


def get_advertisements_in_given_coord_area(coords_lat: float, coords_lng: float, search_radius: int = 10000):
    expression_for_distance = get_search_term_by_distance(coords_lat, coords_lng, search_radius)
    property_type = ['кирпичный', 'железобетонный']
    advertisements = Advertisement.select(Advertisement.coords_lat, Advertisement.coords_lng, Advertisement.url, Price.price).\
        join(Price).join(Parameter, on=(Advertisement.parameter_id==Parameter.id)).join(Property_type).\
        where(expression_for_distance & (Property_type.property_type.in_(property_type))).order_by(Price.price)
    return advertisements


def get_median_price(coords_lat: float, coords_lng: float, search_radius: int = 1000):
    property_type = ['кирпичный', 'железобетонный']
    expression_for_distance = get_search_term_by_distance(coords_lat=coords_lat, coords_lng=coords_lng, search_radius=search_radius)
    prices = Price.select(Price.price).join(Advertisement).join(Parameter).join(Property_type).\
        where(expression_for_distance & (Property_type.property_type.in_(property_type)))
    return int(statistics.median([elm.price for elm in prices]))


if __name__ == "__main__":
    # print(get_search_term_by_parameters(['df', 'fff']))
    delta = 150000
    for advertisement in get_advertisements_in_given_coord_area(55.760973228504646, 49.19055840555971):
        median_price = get_median_price(coords_lat=advertisement.coords_lat, coords_lng=advertisement.coords_lng)
        price = advertisement.price.price
        if price <= 0.87 * median_price - 0.13 * price - delta and price > 10000:
            print(f'Для объявления {advertisement.url} с ценой {price}. Медианная цена ровна {median_price} для объявлений в радиусе {1500} метров')


