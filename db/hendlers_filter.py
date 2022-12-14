import logging
from db.models import db
from db.models import Filter, Type_transaction, Category, Property_type


def add_filter(params: dict):
    Filter.create(**params)


def del_filter_in_bd(filter_id: int) -> None:
    Filter.delete_by_id(pk=filter_id)


def get_filters(user_id: int) -> list[Filter]:
    return Filter.select(Filter, Type_transaction.type_transaction, Category.category, Property_type.property_type).\
        join(Type_transaction, on=(Filter.type_transaction_id == Type_transaction.id)).\
        join(Category, on=(Filter.category_id == Category.id)).\
        join(Property_type, on=(Filter.property_type_id == Property_type.id)).\
        where(Filter.user_id == user_id)


def validation_name_filter(user_id: int, name_filter: str) -> bool:
    f = Filter.select().where(Filter.user_id == user_id & Filter.name_filter == name_filter)
    if f.exists():
        return False
    return True

