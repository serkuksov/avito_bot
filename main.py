#!/usr/bin/env python

import logging
import asyncio
from models import db, set_advertisement, deactivation_advertisement
from avito_parser import AvitoParser
from avito_bot import sending_messages
from handlers_advertisement import checking_filter


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
    url = 'https://www.avito.ru/kazan/garazhi_i_mashinomesta/prodam-ASgBAgICAUSYA~QQ?cd=1&s=104'
    db.connect()
    # db.create_tables([Advertisement, Image, Price, Category, Location])
    try:
        parser = AvitoParser(url)
        for advertisement in parser.get_advertisements_from_all_pages():
            message = set_advertisement(advertisement)
            if message and checking_filter(advertisement=advertisement):
                asyncio.run(sending_messages(message))
        deactivation_advertisement()
    except Exception:
        logging.error('Неудачная попытка парсинга авито')
    finally:
        db.close()


if __name__ == '__main__':
    main()
