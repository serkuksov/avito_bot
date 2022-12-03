from aiogram.utils import executor
from tg_bot.create_bot import dp, bot
from tg_bot.handlers import user


async def on_startup(_):
    print('Бот вышел в онлайн')


async def sending_messages(message: str):
    user_id = 1371107249
    print(user_id)
    await bot.send_message(chat_id=user_id, text=message)


if __name__ == '__main__':
    user.register_handlers_user(dispatcher=dp)
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
