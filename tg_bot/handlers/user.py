from aiogram import types, Dispatcher
from db.handlers_users import create_user, activate_user
from tg_bot.create_bot import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from tg_bot.keyboards.user_kb import kb_start, kb_stop, kb_cancel


class FSMUser(StatesGroup):
    name_filter = State()
    type_transaction_id = State()
    category_id = State()
    parameter_property_type_id = State()
    min_price = State()
    max_price = State()
    coords = State()
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
    text = 'Выберите название фильтра'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_name_filter(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    name_filter = message.text
    async with state.proxy() as data:
        data['name_filter'] = name_filter
    await FSMUser.next()
    text = 'Выберите тип сделки'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_type_transaction_id(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    type_transaction_id = message.text
    async with state.proxy() as data:
        data['type_transaction_id'] = type_transaction_id
    await FSMUser.next()
    # async with state.proxy() as data:
    #     text = str(data)
    text = 'Выберете категорию недвижимости'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)
    # await state.finish()


async def add_category_id(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    category_id = message.text
    async with state.proxy() as data:
        data['category_id'] = category_id
    await FSMUser.next()
    text = 'Выберите параметр недвижимости'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_parameter_property_type_id(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    parameter_property_type_id = message.text
    async with state.proxy() as data:
        data['parameter_property_type_id'] = parameter_property_type_id
    await FSMUser.next()
    text = 'Введите минимальную цену'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)

async def add_min_price(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    min_price = message.text
    async with state.proxy() as data:
        data['min_price'] = min_price
    await FSMUser.next()
    text = 'Введите макисмальную цену'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)

async def add_max_price(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    max_price = message.text
    async with state.proxy() as data:
        data['max_price'] = max_price
    await FSMUser.next()
    text = 'Введите адрес для поиска'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_coords(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    coords = message.text
    coords_lat = None
    coords_lng = None
    async with state.proxy() as data:
        data['coords_lat'] = coords
        data['coords_lng'] = coords
    await FSMUser.next()
    text = 'Введите расстояние в метрах для поиска'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_search_radius(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    search_radius = message.text
    async with state.proxy() as data:
        data['search_radius'] = search_radius
    await FSMUser.next()
    text = 'Введите минимальную площадь недвижимости'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_parameter_property_area_min(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    parameter_property_area_min = message.text
    async with state.proxy() as data:
        data['parameter_property_area_min'] = parameter_property_area_min
    await FSMUser.next()
    text = 'Введите максимальную площадь недвижимости'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)


async def add_parameter_property_area_max(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    parameter_property_area_max = message.text
    async with state.proxy() as data:
        data['parameter_property_area_max'] = parameter_property_area_max
    await FSMUser.next()
    text = 'Введите минимальную доходность при сдаче в аренду'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)

async def add_profitability_rent(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    profitability_rent = message.text
    async with state.proxy() as data:
        data['profitability_rent'] = profitability_rent
    await FSMUser.next()
    text = 'Введите минимальную доходность при перепродаже недвижимости'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_cancel)

async def add_profitability_sale(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    profitability_sale = message.text
    async with state.proxy() as data:
        data['profitability_sale'] = profitability_sale
    text = 'Фильтр успешно создан'
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb_stop)
    async with state.proxy() as data:
        await bot.send_message(chat_id=user_id, text=str(data))
    # await state.finish()


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
    dispatcher.register_message_handler(add_type_transaction_id, state=FSMUser.type_transaction_id)
    dispatcher.register_message_handler(add_category_id, state=FSMUser.category_id)
    dispatcher.register_message_handler(add_type_transaction_id, state=FSMUser.type_transaction_id)
    dispatcher.register_message_handler(add_parameter_property_type_id, state=FSMUser.parameter_property_type_id)
    dispatcher.register_message_handler(add_min_price, state=FSMUser.min_price)
    dispatcher.register_message_handler(add_max_price, state=FSMUser.max_price)
    dispatcher.register_message_handler(add_coords, state=FSMUser.coords)
    dispatcher.register_message_handler(add_search_radius, state=FSMUser.search_radius)
    dispatcher.register_message_handler(add_parameter_property_area_min, state=FSMUser.parameter_property_area_min)
    dispatcher.register_message_handler(add_parameter_property_area_max, state=FSMUser.parameter_property_area_max)
    dispatcher.register_message_handler(add_profitability_rent, state=FSMUser.profitability_rent)
    dispatcher.register_message_handler(add_profitability_sale, state=FSMUser.profitability_sale)

