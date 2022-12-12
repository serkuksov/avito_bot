import logging
from db.models import db
from db.models import Filter


def add_filter(user_id: int, params: dict):
    Filter.create(user_id=user_id, **params)

