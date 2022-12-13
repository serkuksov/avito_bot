import logging
from db.models import db
from db.models import Filter


def add_filter(params: dict):
    Filter.create(**params)


def validation_name_filter(user_id: int, name_filter: str) -> bool:
    f = Filter.select().where(Filter.user_id == user_id & Filter.name_filter == name_filter)
    if f.exists():
        return False
    return True

