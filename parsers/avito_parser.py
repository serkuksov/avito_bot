import logging
import datetime
import json
import time
import urllib.parse
from typing import NamedTuple
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .parser import Parser


class Advertisement(NamedTuple):
    id_avito: int
    url: str
    name: str
    description: str
    category: str
    location: str
    type_transaction: str
    time: datetime.datetime
    price: int
    images: list[str, ...]
    address: str
    geoReferences: list[dict[str, str]]
    phone: bool
    delivery: bool
    message: bool
    parameters: str
    coords_lat: float
    coords_lng: float


class AvitoParser(Parser):
    """Парсер авито. Получение информации со страниц поисковой выдаче"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._get_params_page()
        except NoSuchElementException:
            raise Exception
        self.count_advertisements = self.get_count_advertisements()
        self.count_pages = self.get_count_pages()

    def _get_params_page(self):
        """Получение json с параметрами поисковой выдачи для страницы открытой драйвером"""
        try:
            # TODO требуется заменить на метод ожидания появления элемента на странице
            params = self.driver.find_element(By.XPATH, '//script[contains(text(), "window.__initialData__")]'). \
                get_attribute("outerHTML")
        except:
            time.sleep(2)
            try:
                params = self.driver.find_element(By.XPATH, '//script[contains(text(), "window.__initialData__")]'). \
                    get_attribute("outerHTML")
            except:
                logging.error(f'На странице {self.url} не найден элемент XPATH')
                raise Exception
        params = params.split('"')[1]
        params = urllib.parse.unquote(params)
        params = json.loads(params)
        # Сохранение json для отладки проекта
        with open('./test1.json', 'w', encoding='utf-8') as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
        for elm in params.keys():
            if '@avito/bx-single-page' in elm:
                self.params = params[elm]

    def get_count_advertisements(self) -> int:
        """Получить количество объявлений в поисковой выдаче"""
        count_advertisements = self.params['data']['count']
        logging.info(f'Всего: {count_advertisements} объявлений')
        return count_advertisements

    def get_count_pages(self) -> int:
        """Получить количество страниц в поисковой выдаче"""
        count_pages = self.count_advertisements // 50 + 1
        logging.info(f'Всего: {count_pages} страниц')
        return count_pages

    def get_next_url_page(self):
        """Генератор ссылок на последующие страницы поисковой выдачи"""
        page = 2
        for i in range(50, self.count_advertisements, 50):
            url_page = f'{self.url}?p={page}'
            logging.info(f'Получено ссылок {page} из {self.count_pages}')
            yield url_page
            page += 1

    def get_advertisements_from_one_page(self) -> Advertisement:
        """Генератор объявлений полученых с текущей страницы"""
        for item in self.params['data']['catalog']['items']:
            try:
                if 'kuplyu' in item['urlPath'] or 'snimu' in item['urlPath']:
                    logging.debug(f'Пропущено объявление с типом сделки куплю/сниму: '
                                  f'https://www.avito.ru{item["urlPath"]}')
                    continue
                name = item['title'].replace(' ', ' ')
                if name == '':
                    raise ValueError
                advertisement = Advertisement(
                    id_avito=item['id'],
                    url='https://www.avito.ru' + item['urlPath'],
                    name=name,
                    description=self._get_description(item),
                    category=item['category']['name'],
                    location=item['location']['name'],
                    type_transaction=self._get_type_transaction(item['priceDetailed']['postfix']),
                    time=self._get_time_advertisement(item),
                    price=item['priceDetailed']['value'],
                    images=[image['636x476'] for image in item['images']],
                    address=item['geo']['formattedAddress'],
                    geoReferences=self._get_georeferences(item),
                    phone=item['contacts']['phone'],
                    delivery=item['contacts']['delivery'],
                    message=item['contacts']['message'],
                    parameters=self._get_parametrs_advertisement(item),
                    coords_lat=item['coords']['lat'],
                    coords_lng=item['coords']['lng']
                )
                logging.debug(f'Получены параметры объявления: {advertisement.url}')
                yield advertisement
            except KeyError:
                if item.get('code'):
                    continue
                logging.error(f'Не найден ключ при разборе json полученного с {self.url}')
            except ValueError:
                logging.error(f'У объявления нет названия {self.url}')
                continue

    def _get_description(self, item):
        try:
            return item['description'].replace(' ', ' ').replace('\n', ' ').strip()
        except AttributeError:
            return ''

    def _get_type_transaction(self, postfix: str) -> str:
        if postfix == '':
            return 'Купить'
        elif 'месяц' in postfix:
            return 'Снять на месяц'
        elif 'сутки' in postfix:
            return 'Снять на день'

    def _get_georeferences(self, item: dict) -> list[dict[str, str]]:
        geoReferences = []
        for geo in item['geo']['geoReferences']:
            after = geo.get('after')
            if after is None:
                after = ''
            else:
                after = after.replace(' ', ' ').strip()
            geoReferences.append({'content': geo['content'], 'after': after})
        return geoReferences

    def _get_parametrs_advertisement(self, item: dict) -> str:
        # возможно стоит убрать 0 если много параметров
        try:
            parametrs_advertisement = item['iva']['AutoParamsStep'][0]['payload']['text']
        except IndexError:
            return ''
        if parametrs_advertisement is None:
            return ''
        return parametrs_advertisement

    def _get_time_advertisement(self, item: dict) -> datetime:
        return datetime.datetime.fromtimestamp(item['sortTimeStamp'] // 1000)

    def get_advertisements_from_all_pages(self) -> Advertisement:
        """Генератор объявлений полученых со всех страниц поисковой выдачи"""
        for advertisement in self.get_advertisements_from_one_page():
            yield advertisement
        for url_page in self.get_next_url_page():
            try:
                self.open_new_page(url_page)
                for advertisement in self.get_advertisements_from_one_page():
                    yield advertisement
            except:
                raise Exception
                # continue

    def open_new_page(self, *args, **kwargs):
        """Дополнительно получаем параметры со страницы"""
        super().open_new_page(*args, **kwargs)
        self._get_params_page()
