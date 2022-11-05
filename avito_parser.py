import logging
import datetime
import json
import urllib.parse
from selenium.webdriver.common.by import By
from parser import Parser


class Avito_parser(Parser):
    """Парсер авито. Получение информации со страниц поисковой выдаче"""

    def _get_data(self):
        script = self.driver.find_element(By.XPATH, '//script[contains(text(), "window.__initialData__")]').get_attribute("outerHTML")
        script = script.split('"')[1]
        if script:
            script = urllib.parse.unquote(script)
            script = json.loads(script)
            for elm in script.keys():
                if '@avito/bx-single-page' in elm:
                    data = script[elm]['data']
                    with open('test1.json', 'w', encoding='utf-8') as f:
                        json.dump(script, f, ensure_ascii=False, indent=2)
                    return data

    def get_pages(self):
        data = self._get_data()
        count = data['count']
        logging.info(f'Найдено {count} объявлений')
        pages = []
        for page in data['catalog']['pager']['pages'].values():
            pages.append('https://www.avito.ru' + page)
        return pages

    def get_advertisements(self):
        data = self._get_data()
        for item in data['catalog']['items']:
            if item.get('id'):
                geoReferences = []
                for geo in item['geo']['geoReferences']:
                    after = geo.get('after')
                    if after == None:
                        after = ''
                    else:
                        after = after.replace(' ', ' ')
                    geoReferences.append({'content': geo['content'], 'after': after})
                try:
                    parameters = str(item['iva']['AutoParamsStep'][0]['payload']['text']) #возможно стоит убрать 0 если много параметров
                except:
                    parameters = ''
                advertisements = {
                                    'id_avito': item['id'],
                                    'url': 'https://www.avito.ru' + item['urlPath'],
                                    'name': item['title'].replace(' ', ' '),
                                    'description': self.get_description(item),
                                    'category': item['category']['name'],
                                    'location': item['location']['name'],
                                    'time': datetime.datetime.fromtimestamp(item['sortTimeStamp']//1000),
                                    'price': item['priceDetailed']['value'],
                                    'images': [image['636x476'] for image in item['images']],
                                    'address': item['geo']['formattedAddress'],
                                    'geoReferences': geoReferences,
                                    'phone': item['contacts']['phone'],
                                    'delivery': item['contacts']['delivery'],
                                    'message': item['contacts']['message'],
                                    'parameters': parameters,
                                    'coords_lat': item['coords']['lat'],
                                    'coords_lng': item['coords']['lng']
                                 }
                yield advertisements

    def get_description(self, item):
        try:
            return item['description'].replace(' ', ' ').replace('\n', ' ')
        except AttributeError:
            return ''





