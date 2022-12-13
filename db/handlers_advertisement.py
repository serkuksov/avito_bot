import re
import logging
import statistics
from peewee import Expression
from db.models import *
from parsers.avito_parser import Advertisement as Ad_avito

SEARCH_RADIUS_FO_CALC_MEDIAN_PRICE = 1000

def get_property_area(name: str) -> int:
    property_area = re.findall(r'\d+', name)
    if property_area:
        return int(property_area[0])


def get_parameters_in_dict(parameters: str) -> dict:
    """Преобразовать строку параметров для объявления в словарь"""
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
    if advertisement.category == 'Гаражи и машиноместа':
        dict_params = get_parameters_in_dict(advertisement.parameters)
        property_area = get_property_area(advertisement.name)
        property_type_id = get_property_type_id(dict_params['property_type'])
        if property_type_id is None:
            property_type_id = create_property_type(dict_params['property_type'])
        security = dict_params['security']
        parameter_id = Parameter.create(property_type_id=property_type_id, property_area=property_area, security=security)
        return parameter_id


def create_advertisement(advertisement: Ad_avito):
    """Добавляет новое объявление"""
    category_id = get_category_id(category=advertisement.category)
    if category_id is None:
        category_id = create_category(category=advertisement.category)
    type_transaction_id = get_type_transaction_id(type_transaction=advertisement.type_transaction)
    if type_transaction_id is None:
        type_transaction_id = create_type_transaction(type_transaction=advertisement.type_transaction)
    ad = Advertisement(
        id_avito=advertisement.id_avito,
        url=advertisement.url,
        name=advertisement.name,
        description=advertisement.description,
        category_id=category_id,
        location_id=get_location_id(location=advertisement.location),
        type_transaction_id=type_transaction_id,
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


def get_category_id(category: str) -> int:
    """Получить id категорри, если нет вернуть None"""
    category_id = Category.select().where(Category.category == category)
    if category_id.exists():
        return category_id.get().id

def get_list_category() -> list[tuple]:
    """Получить список кортежей в формате id, название категории"""
    list_category = [(c.id, c.category) for c in Category.select(Category.id, Category.category)]
    return list_category

def create_category(category: str) -> int:
    """Создать новую категорию и вернуть id"""
    category_id = Category.create(category=category).id
    return category_id


def get_type_transaction_id(type_transaction: str) -> int:
    """Получить id типа сделки, если нет вернуть None"""
    type_transaction_id = Type_transaction.select().where(Type_transaction.type_transaction == type_transaction)
    if type_transaction_id.exists():
        return type_transaction_id.get().id


def get_list_types_transactions() -> list[tuple[int, str]]:
    """Получить список кортежей с id и типами сделок"""
    type_transaction = [(t.id, t.type_transaction) for t in Type_transaction.select(Type_transaction.id, Type_transaction.type_transaction)]
    return type_transaction


def create_type_transaction(type_transaction: str) -> int:
    """Добавить новый тип в БД и вернуть id"""
    type_transaction_id = Type_transaction.create(type_transaction=type_transaction).id
    return type_transaction_id


def get_location_id(location: str) -> int:
    """Получить id локации, если нет создать новую категорию и вернуть id"""
    try:
        location_id = Location.get(Location.location == location)
    except:
        location_id = Location.create(location=location).id
    return location_id


def get_property_type_id(property_type: str) -> int:
    """Получить id типа недвижимости, если нет вернуть None"""
    property_type_id = Property_type.select().where(Property_type.property_type == property_type)
    if property_type_id.exists():
        return property_type_id.get().id


def get_list_property_type() -> list[tuple]:
    """Получить список кортежей с id и типами недвижимости"""
    list_property_type = [(p.id, p.property_type) for p in Property_type.select(Property_type.id, Property_type.property_type)]
    return list_property_type


def create_property_type(property_type: str) -> int:
    """Создать новый тип и вернуть id"""
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
    date_update = datetime.datetime.now() - datetime.timedelta(hours=6)
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


def get_median_price(coords_lat: float, coords_lng: float, search_radius: int = SEARCH_RADIUS_FO_CALC_MEDIAN_PRICE):
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
            print(f'Для объявления {advertisement.url} с ценой {price}. Медианная цена ровна {median_price} для объявлений в радиусе {1000} метров')



