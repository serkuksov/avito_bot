#!/usr/bin/env python
import logging
from aiogram.utils import executor
from tg_bot.create_bot import dp, bot
from tg_bot.handlers import user


def log():
    """Логирование скрипта в консоль и файл"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.FileHandler('Бот.log', 'a', 'utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    handler.setLevel(logging.INFO)
    root_logger.addHandler(handler)


async def on_startup(_):
    pass
    # print('Бот вышел в онлайн')


if __name__ == '__main__':
    log()
    user.register_handlers_user(dispatcher=dp)
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
