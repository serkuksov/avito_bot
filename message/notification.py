from parsers.avito_parser import Advertisement


# TODO требуется прописать функционал для формирования сообщений. Убрать текущую реализацию
class Notification:
    """Класс содержащий параметры сообщения для отправки в телеграмм"""

    def __init__(self, advertisement: Advertisement):
        self.advertisement = Advertisement
        self.status = None
        self.price_change = None
        self.profitability_rent = None
        self.profitability_sale = None
        self.profitability_sale = None
        self.median_price = None

    def set_status(self, status):
        self.status = status

    def set_price_change(self, price_change):
        self.price_change = price_change

    def set_profitability_rent(self, profitability_rent):
        self.profitability_rent = profitability_rent

    def set_profitability_sale(self, profitability_sale):
        self.profitability_sale = profitability_sale

    def create_message(self):
        message = f'{self.status} <a href="{self.advertisement.url}">{self.advertisement.name}</a>.\n'
        message += f'Расположен по адресу: {self.advertisement.location} {self.advertisement.address}.\n'
        if self.price_change:
            message += f'Изменение цены: {self.price_change}.\n'
        message += f'Медианная цена: {self.profitability_sale}.\n'
        message += f'Доходность аренды: {self.profitability_rent}.\n'
        message += f'Доходность продажи: {self.profitability_sale}.\n'
        return message
