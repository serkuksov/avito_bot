from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b_activate_user = KeyboardButton('Активировать рассылку')
b_deactivate_user = KeyboardButton('Деактивировать рассылку')
b_add_filter = KeyboardButton('Создать новый фильтр')
b_get_filters = KeyboardButton('Показать все фильтры')
b_cancel = KeyboardButton('Отменить')
b_next = KeyboardButton('Пропустить')

kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_start.add(b_activate_user)

kb_stop = ReplyKeyboardMarkup(resize_keyboard=True)
kb_stop.add(b_deactivate_user).add(b_add_filter).add(b_get_filters)

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
kb_cancel.add(b_cancel)

kb_cancel_and_next = ReplyKeyboardMarkup(resize_keyboard=True)
kb_cancel_and_next.add(b_next).add(b_cancel)
