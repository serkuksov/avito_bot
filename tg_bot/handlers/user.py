from aiogram import types, Dispatcher
from db.handlers_users import create_user, activate_user
from tg_bot.create_bot import dp, bot


async def add_new_user_and_activate(message: types.Message):
    user_id = message.from_user.id
    message = create_user(user_id=user_id)
    await bot.send_message(chat_id=user_id, text=message)


async def deactivate_user(message: types.Message):
    user_id = message.from_user.id
    message = activate_user(user_id=user_id, activate=False)
    await bot.send_message(chat_id=user_id, text=message)


def register_handlers_user(dispatcher: Dispatcher):
    dispatcher.register_message_handler(add_new_user_and_activate, commands=['start', 'Старт'])
    dispatcher.register_message_handler(deactivate_user, commands=['stop', 'Стоп'])
