import logging
from db.models import db
from db.models import User_tg, Filter

def create_user(user_id):
    with db:
        try:
            User_tg.create(tg_id=int(user_id)).save()
            message = 'Пользователь добавлен к рассылке'
        except:
            message = 'Пользователь уже добавлен'
        logging.info(message)
        return message