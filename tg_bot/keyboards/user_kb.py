from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b_activate_user = KeyboardButton('/Активировать_рассылку')
b_deactivate_user = KeyboardButton('/Деактивировать_рассылку')
b_add_filter = KeyboardButton('/Создать_новый_фильтр')
b_cancel = KeyboardButton('/Отменить')

kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_start.add(b_activate_user)

kb_stop = ReplyKeyboardMarkup(resize_keyboard=True)
kb_stop.add(b_deactivate_user).add(b_add_filter)

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
kb_cancel.add(b_cancel)

