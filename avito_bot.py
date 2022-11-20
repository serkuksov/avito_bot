from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def echo_send(message: types.Message):
    user_id = message.from_user.id
    await bot.send_message(chat_id=user_id, text=f'Пользователь добавлен к рассылке')


async def sending_messages(message: str):
    user_id = 1371107249
    print(user_id)
    await bot.send_message(chat_id=user_id, text=message)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
