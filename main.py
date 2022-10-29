import datetime
import logging
import peewee
from models import db, Advertisement
from avito_parser import Avito_parser

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
    url ='https://www.avito.ru/kazan/garazhi_i_mashinomesta/prodam/garazh-ASgBAgICAkSYA~QQqAjsVQ?f=ASgBAQECAkSYA~QQqAjsVQFAngwk3qsB4qsBAUXGmgwZeyJmcm9tIjoxMDAwLCJ0byI6MjUwMDAwfQ&i=1&s=104'
    db.connect()
    db.create_tables([Advertisement])
    parser = Avito_parser(url)
    pages = parser.get_pages()
    i = 1
    for url_page in pages:
        if url_page != url:
            parser.open_new_page(url_page)
        advertisements = parser.get_advertisements()
        for advertisement in advertisements:
            try:
                Advertisement.create(**advertisement)
            except peewee.IntegrityError:
                elm = Advertisement.get(Advertisement.id_avito == advertisement['id_avito'])
                if advertisement['price'] != elm.price:
                    price_difference = elm.price - advertisement['price']
                    elm.price = advertisement['price']
                    if price_difference > 0:
                        print(f'Снижение цены для {advertisement["url"]} на {price_difference}')
                elm.date_update = datetime.datetime.now()
                elm.save()
        logging.info(f'Просмотрено {i} страниц из {len(pages)}')
        i += 1
    db.close()

if __name__ == '__main__':
    main()