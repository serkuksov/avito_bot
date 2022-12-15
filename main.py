#!/usr/bin/env python
import asyncio
import logging
from db.hendlers_filter import get_users_id_after_check_filters
from db.models import *
from db.handlers_advertisement import set_advertisement, deactivation_advertisement, get_profitability_sale, \
    get_profitability_rent
from parsers.avito_parser import AvitoParser
from tg_bot.handlers.user import sending_messages_users


def log():
    """Логирование скрипта в консоль и файл"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.FileHandler('Протокол.log', 'a', 'utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    handler.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    logging.getLogger("selenium").setLevel(logging.ERROR)
    logging.getLogger("webdriver_manager").setLevel(logging.ERROR)


def main():
    log()
    urls = [
            # 'https://www.avito.ru/kazan/garazhi_i_mashinomesta',
            # 'https://www.avito.ru/kazan/zemelnye_uchastki',
            'https://www.avito.ru/kazan/doma_dachi_kottedzhi'
            ]
    # db.connect()
    # db.create_tables([Advertisement, Image, Price, Category, Location, Property_type, Parameter, User_tg, Filter])
    # db.close()
    for url in urls:
        try:
            parser = AvitoParser(url)
            for advertisement in parser.get_advertisements_from_all_pages():
                try:
                    message = set_advertisement(advertisement)
                except Exception as ex:
                    logging.error(f'Не удалось записать объявление в базу. Ошибка: {ex}')
                    continue
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
                        asyncio.run(sending_messages_users(users_id=users_id, message=message))
            deactivation_advertisement()
        except Exception as ex:
            logging.error(f'Неудачная попытка парсинга авито, {ex}')
            logging.exception()


if __name__ == '__main__':
    main()
