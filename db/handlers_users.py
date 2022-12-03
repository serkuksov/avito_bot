import logging
from db.models import db
from db.models import User_tg, Filter


def create_user(user_id: int) -> str:
    with db:
        try:
            User_tg.create(tg_id=user_id).save()
            message = 'Пользователь добавлен к рассылке'
        except:
            message = activate_user(user_id=user_id, activate=True)
        logging.info(f'{message} - ID={user_id}')
        return message


def activate_user(user_id: int, activate: bool = True) -> str:
    with db:
        user = User_tg.get(tg_id=user_id)
        user.activated = activate
        user.save()
        if activate:
            message = 'Пользователь активирован'
        else:
            message = 'Пользователь деактивирован'
        logging.info(f'{message} - ID={user_id}')
        return message

