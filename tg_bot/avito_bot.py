from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from db.handlers_users import create_user
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def create_new_user(message: types.Message):
    user_id = message.from_user.id
    message = create_user(user_id=user_id)
    await bot.send_message(chat_id=user_id, text=message)


async def sending_messages(message: str):
    user_id = 1371107249
    print(user_id)
    await bot.send_message(chat_id=user_id, text=message)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
