#!/usr/bin/env python
from aiogram.utils import executor
from tg_bot.create_bot import dp, bot
from tg_bot.handlers import user


async def on_startup(_):
    pass
    # print('Бот вышел в онлайн')


if __name__ == '__main__':
    user.register_handlers_user(dispatcher=dp)
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
