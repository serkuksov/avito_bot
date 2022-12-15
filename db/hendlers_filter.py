from peewee import Expression, JOIN
from db.handlers_advertisement import get_parameters_in_dict, get_property_area_from_advertisement
from db.models import Filter, Type_transaction, Category, Property_type
from parsers.avito_parser import Advertisement


def add_filter(params: dict):
    Filter.create(**params)


def del_filter_in_bd(filter_id: int) -> None:
    Filter.delete_by_id(pk=filter_id)


def get_filters(user_id: int) -> list[Filter]:
    return Filter.select(Filter, Type_transaction.type_transaction, Category.category, Property_type.property_type).\
        join(Type_transaction, on=(Filter.type_transaction_id == Type_transaction.id)).\
        join(Category, on=(Filter.category_id == Category.id)).\
        join(Property_type, JOIN.LEFT_OUTER, on=(Filter.property_type_id == Property_type.id)).\
        where(Filter.user_id == user_id)


def validation_name_filter(user_id: int, name_filter: str) -> bool:
    f = Filter.select().where((Filter.user_id == user_id) & (Filter.name_filter == name_filter))
    if f.exists():
        return False
    return True


def get_search_term_by_distance(coords_lat: float, coords_lng: float) -> Expression:
    expression_for_distance = ((coords_lat - Filter.coords_lat) * (coords_lat - Filter.coords_lat) +
                (coords_lng - Filter.coords_lng) * (coords_lng - Filter.coords_lng)) \
               * 111000 * 111000 <= Filter.search_radius * Filter.search_radius
    return expression_for_distance


def get_users_id_after_check_filters(advertisement: Advertisement,
                                     profitability_rent: int = 0,
                                     profitability_sale: int = 0) -> list[int]:
    property_type = get_parameters_in_dict(advertisement.parameters)['property_type']
    property_area = get_property_area_from_advertisement(advertisement)
    expression_for_distance = get_search_term_by_distance(advertisement.coords_lat, advertisement.coords_lng)
    filters = Filter.select(Filter.user_id).distinct().\
        join(Type_transaction, on=(Filter.type_transaction_id == Type_transaction.id)).\
        join(Category, on=(Filter.category_id == Category.id)).\
        join(Property_type, on=(Filter.property_type_id == Property_type.id)).\
        where((Filter.category_id.category == advertisement.category) &
              (Filter.type_transaction_id.type_transaction == advertisement.type_transaction) &
              (Filter.property_type_id.property_type == property_type) &
              (Filter.min_price <= advertisement.price) &
              (Filter.max_price >= advertisement.price) &
              (Filter.parameter_property_area_min <= property_area) &
              (Filter.parameter_property_area_max >= property_area) &
              ((Filter.profitability_rent <= profitability_rent) |
              (Filter.profitability_sale <= profitability_sale)) &
              expression_for_distance)
    users_id = [f.user_id for f in filters]
    return users_id
