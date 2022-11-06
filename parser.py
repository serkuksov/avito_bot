import logging
import time
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webelement import WebElement


class Parser:
    """Открывает браузер (хром) заходит на сайт"""
    def __init__(self, url, login=None, password=None, timeout=2):
        self.url = url
        self.login = login
        self.password = password
        self.timeout = timeout
        try:
            caps = DesiredCapabilities().CHROME
            # caps["pageLoadStrategy"] = "normal"  # complete
            caps["pageLoadStrategy"] = "eager"  #  interactive
            # caps["pageLoadStrategy"] = "none"
            option = ChromeOptions()
            # option.add_experimental_option('dom.webdriver.enabled', False)
            option.add_argument("--disable-blink-features=AutomationControlled")
            option.add_argument('--log-level=50')
            option.add_argument("--start-maximized")
            option.add_argument('--headless')
            option.add_argument('--no-sandbox')
            option.add_argument('--disable-dev-shm-usage')
            option.headless = True
            option.add_experimental_option('prefs', {
                # "download.default_directory": "C:/Users/517/Download", #Change default directory for downloads
                # "download.prompt_for_download": False, #To auto download the file
                # "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
            })
            self.driver = Chrome(service=Service(ChromeDriverManager().install()),
                                 options=option,
                                 desired_capabilities=caps)
            logging.info(f'Браузер открыт')
        except:
            logging.error('Ошибка браузера!!! Веб драйвер не работает')
            raise Exception()
        try:
            self.driver.get(self.url)
            logging.info(f'Открываю страницу: {self.url}')
            time.sleep(self.timeout)
        except:
            logging.error('Ошибка браузера!!! Не удалось открыть сайт')
            raise Exception()

    def __del__(self):
        self.driver.close()
        # self.driver.quit()
        logging.info(f'Браузер закрыт')

    def get_html_elm(self, elm: WebElement) -> str:
        """Получить HTML код выбраного элнмента"""
        return elm.get_attribute("outerHTML")

    def get_html_page(self) -> str:
        """Получить HTML код страницы"""
        return self.driver.page_source

    def open_new_page(self, url: str) -> None:
        """Метод открывает новую страницу в браузере"""
        logging.info(f'Открываю страницу: {url}')
        self.driver.get(url)
        time.sleep(self.timeout)




