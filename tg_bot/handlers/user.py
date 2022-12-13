from aiogram import types, Dispatcher
from geopy import Nominatim
from db.handlers_users import create_user, activate_user
from db.handlers_advertisement import get_list_types_transactions, get_list_category, get_list_property_type
from db.hendlers_filter import validation_name_filter, add_filter
from tg_bot.create_bot import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from tg_bot.keyboards.user_kb import kb_start, kb_stop, kb_cancel
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class FSMUser(StatesGroup):
    name_filter = State()
    type_transaction_id = State()
    category_id = State()
    parameter_property_type_id = State()
    min_price = State()
    max_price = State()
    coords = State()
    check_coords = State()
    search_radius = State()
    parameter_property_area_min = State()
    parameter_property_area_max = State()
    profitability_rent = State()
    profitability_sale = State()


async def add_new_user_and_activate(message: types.Message):
    user_id = message.from_user.id
    text = create_user(user_id=user_id)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_stop)


async def deactivate_user(message: types.Message):
    user_id = message.from_user.id
    text = activate_user(user_id=user_id, activate=False)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_start)


async def create_filter(message: types.Message, state: FSMContext):
    await FSMUser.name_filter.set()
    user_id = message.from_user.id
    async with state.proxy() as data:
        data['user_id'] = user_id
    text = 'Введите название фильтра'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_name_filter(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    name_filter = message.text
    if validation_name_filter(user_id=user_id, name_filter=name_filter):
        async with state.proxy() as data:
            data['name_filter'] = name_filter
        await FSMUser.next()
        text = 'Выберите тип сделки'
        in_keyboard = InlineKeyboardMarkup()
        for type_transaction_id, type_transaction in get_list_types_transactions():
            in_keyboard.add(InlineKeyboardButton(text=type_transaction, callback_data=str(type_transaction_id)))
        await bot.send_message(chat_id=user_id, text=text, reply_markup=in_keyboard)
    else:
        text = 'Наименование фильтра не уникальное. Введите новое наименование.'
        await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_type_transaction_id(call: types.CallbackQuery, state: FSMContext):
    type_transaction_id = call.data
    async with state.proxy() as data:
        data['type_transaction_id'] = type_transaction_id
    await FSMUser.next()
    in_keyboard = InlineKeyboardMarkup()
    for category_id, category in get_list_category():
        in_keyboard.add(InlineKeyboardButton(text=category, callback_data=str(category_id)))
    text = 'Выберете категорию недвижимости'
    await call.message.answer(text=text, reply_markup=in_keyboard)
    await call.answer()


async def add_category_id(call: types.CallbackQuery, state: FSMContext):
    category_id = call.data
    async with state.proxy() as data:
        data['category_id'] = category_id
    await FSMUser.next()
    in_keyboard = InlineKeyboardMarkup()
    for property_type_id, property_type in get_list_property_type():
        in_keyboard.add(InlineKeyboardButton(text=property_type, callback_data=str(category_id)))
    text = 'Выберите параметр недвижимости'
    await call.message.answer(text=text, reply_markup=in_keyboard)
    await call.answer()


async def add_parameter_property_type_id(call: types.CallbackQuery, state: FSMContext):
    property_type_id = call.data
    async with state.proxy() as data:
        data['property_type_id'] = property_type_id
    await FSMUser.next()
    text = 'Введите минимальную цену'
    await call.message.answer(text=text)
    await call.answer()


async def add_min_price(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        min_price = int(message.text)
        async with state.proxy() as data:
            data['min_price'] = min_price
        await FSMUser.next()
        text = 'Введите макисмальную цену'
    except ValueError:
        text = 'Цена введена не корректно. Введите минимальную цену повторно'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_max_price(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        max_price = int(message.text)
        async with state.proxy() as data:
            data['max_price'] = max_price
        await FSMUser.next()
        text = 'Введите адрес для поиска'
    except ValueError:
        text = 'Цена введена не корректно. Введите макисмальную цену повторно'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_coords(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    geolocator = Nominatim(user_agent='avito_parser')
    location = geolocator.geocode(message.text)
    try:
        coords_lat = location.latitude
        coords_lng = location.longitude
        async with state.proxy() as data:
            data['coords_lat'] = coords_lat
            data['coords_lng'] = coords_lng
        await FSMUser.next()
        text = f'Адрес: "{location.address}" определен верно?'
        in_keybord = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Да', callback_data='Да'),
            InlineKeyboardButton(text='Нет', callback_data='Нет')
        )
        await bot.send_message(chat_id=user_id, text=text, reply_markup=in_keybord)
    except AttributeError:
        text = f'Адрес не найден, попробуйте ввести в другом виде'
        await bot.send_message(chat_id=user_id, text=text)


async def check_coords(call: types.CallbackQuery):
    if call.data == 'Да':
        await FSMUser.next()
        text = 'Введите расстояние в метрах для поиска'
    elif call.data == 'Нет':
        await FSMUser.previous()
        text = 'Введите адрес для поиска заново'
    else:
        text = 'Используйте инлайн кнопки'
    await call.message.answer(text=text)
    await call.answer()


async def add_search_radius(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        search_radius = int(message.text)
        async with state.proxy() as data:
            data['search_radius'] = search_radius
        await FSMUser.next()
        text = 'Введите минимальную площадь недвижимости'
    except ValueError:
        text = 'Расстояние введено не корректно. Введите радиус поиска в метрах повторно'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_parameter_property_area_min(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        parameter_property_area_min = int(message.text)
        async with state.proxy() as data:
            data['parameter_property_area_min'] = parameter_property_area_min
        await FSMUser.next()
        text = 'Введите максимальную площадь недвижимости'
    except ValueError:
        text = 'Площадь введена не корректно. Введите минимальную площадь повторно'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_parameter_property_area_max(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        parameter_property_area_max = int(message.text)
        async with state.proxy() as data:
            data['parameter_property_area_max'] = parameter_property_area_max
        await FSMUser.next()
        text = 'Введите минимальную доходность при сдаче в аренду'
    except ValueError:
        text = 'Площадь введена не корректно. Введите максимальную площадь повторно'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_profitability_rent(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        profitability_rent = int(message.text)
        async with state.proxy() as data:
            data['profitability_rent'] = profitability_rent
        await FSMUser.next()
        text = 'Введите минимальную доходность при перепродаже недвижимости'
    except ValueError:
        text = 'Доходность введена не корректно. Введите минимальную доходность при сдаче в аренду повторно'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_profitability_sale(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        profitability_sale = int(message.text)
        async with state.proxy() as data:
            data['profitability_sale'] = profitability_sale
            add_filter(params=data)
        text = 'Фильтр успешно создан'
    except ValueError:
        text = 'Доходность введена не корректно. Введите минимальную доходность при перепродаже недвижимости повторно'
    await state.finish()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_stop)


async def cancel(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = 'Действие отменено!'
    await state.finish()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_stop)


def register_handlers_user(dispatcher: Dispatcher):
    dispatcher.register_message_handler(add_new_user_and_activate, commands=['start', 'Активировать_рассылку'])
    dispatcher.register_message_handler(deactivate_user, commands=['Деактивировать_рассылку'])
    dispatcher.register_message_handler(create_filter, commands=['Создать_новый_фильтр'], state=None)
    dispatcher.register_message_handler(cancel, commands=['Отменить'], state="*")
    dispatcher.register_message_handler(add_name_filter, state=FSMUser.name_filter)
    dispatcher.register_callback_query_handler(add_type_transaction_id, state=FSMUser.type_transaction_id)
    dispatcher.register_callback_query_handler(add_category_id, state=FSMUser.category_id)
    dispatcher.register_callback_query_handler(add_parameter_property_type_id, state=FSMUser.parameter_property_type_id)
    dispatcher.register_message_handler(add_min_price, state=FSMUser.min_price)
    dispatcher.register_message_handler(add_max_price, state=FSMUser.max_price)
    dispatcher.register_message_handler(add_coords, state=FSMUser.coords)
    dispatcher.register_callback_query_handler(check_coords, state=FSMUser.check_coords)
    dispatcher.register_message_handler(add_search_radius, state=FSMUser.search_radius)
    dispatcher.register_message_handler(add_parameter_property_area_min, state=FSMUser.parameter_property_area_min)
    dispatcher.register_message_handler(add_parameter_property_area_max, state=FSMUser.parameter_property_area_max)
    dispatcher.register_message_handler(add_profitability_rent, state=FSMUser.profitability_rent)
    dispatcher.register_message_handler(add_profitability_sale, state=FSMUser.profitability_sale)
