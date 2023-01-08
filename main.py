#!/usr/bin/env python
import asyncio
import logging
import time
import requests
from config import TOKEN
from db.hendlers_filter import get_users_id_after_check_filters
from db.models import *
from db.handlers_advertisement import set_advertisement, deactivation_advertisement, get_profitability_sale, \
    get_profitability_rent
from parsers.avito_parser import AvitoParser


def log():
    """Логирование скрипта в консоль и файл"""
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.FileHandler('Протокол.log', 'a', 'utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    handler.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    logging.getLogger("selenium").setLevel(logging.ERROR)
    logging.getLogger("webdriver_manager").setLevel(logging.ERROR)


def sending_messages_users(users_id: list[int], message: str):
    """Отправка сообщений в ТГ"""
    for user_id in users_id:
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
        print(url)
        data = {'chat_id': user_id,
                'text': message}
        r = requests.post(url=url, data=data)
        if r.status_code != 200:
            logging.error('Не удалось отправить сообщение в телеграмм')
        else:
            logging.info(f'Сообщение пользователю с id={user_id} направлено')


def main():
    log()
    urls = [
            'https://www.avito.ru/kazan/garazhi_i_mashinomesta',
            'https://www.avito.ru/kazan/zemelnye_uchastki',
            'https://www.avito.ru/kazan/doma_dachi_kottedzhi'
            ]
    # db.connect()
    # db.create_tables([Advertisement, Image, Price, Category, Location, Property_type, Parameter, User_tg, Filter,
    #                   Characteristic, Characteristic_values, Characteristics_set_for_advertisement])
    # db.close()
    for url in urls:
        try:
            parser = AvitoParser(url)
            for advertisement in parser.get_advertisements_from_all_pages():
                try:
                    message = set_advertisement(advertisement)
                except Exception as ex:
                    logging.error(f'Не удалось записать объявление в базу. Ошибка: {ex} для {advertisement.url}')
                    raise
                    continue
                # todo необходимо формирование сообщений вынести в отдельныей файл
                if message:
                    profitability_rent = get_profitability_rent(advertisement)
                    profitability_sale = get_profitability_sale(advertisement)
                    if advertisement.type_transaction == 'Купить':
                        message += f'\nОжидаемая доходность аренды {profitability_rent} %.\n' \
                                   f'Ожидаемая доходность продажи {profitability_sale} %.'
                        print(message)
                    users_id = get_users_id_after_check_filters(advertisement,
                                                                profitability_rent=profitability_rent,
                                                                profitability_sale=profitability_sale)
                    if users_id:
                        sending_messages_users(users_id=users_id, message=message)
        except Exception as ex:
            logging.error(f'Неудачная попытка парсинга авито, {ex}')
            logging.exception('')
        finally:
            del parser
        time.sleep(20)
    try:
        deactivation_advertisement()
    except Exception as ex:
        logging.exception(ex)


if __name__ == '__main__':
    try:
        main()
    except:
        exit()
