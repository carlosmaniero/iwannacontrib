import os
import stat
from sys import platform
from zipfile import ZipFile

import requests
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

CHROME_URL_MAC = 'https://chromedriver.storage.googleapis.com/84.0.4147.30/chromedriver_mac64.zip'
CHROME_URL_LINUX = 'https://chromedriver.storage.googleapis.com/84.0.4147.30/chromedriver_linux64.zip'
CHROME_DIR = '.chrome'
CHROME_DRIVER_PATH = '.chrome/chromedriver'
CHROME_ZIP_PATH = '.chrome/driver.zip'


class E2ETesting(LiveServerTestCase):

    def __init__(self, *args, **kwargs):
        super(E2ETesting, self).__init__(*args, **kwargs)

        if not os.path.exists(CHROME_DIR):
            self._download_chrome()

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        self.webdriver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)

    def tearDown(self) -> None:
        self.webdriver.close()
        self.webdriver.quit()

    def fetch(self, url):
        url = f'{self.live_server_url}{url}'
        self.webdriver.get(url)

    def _download_chrome(self):
        if not os.path.exists(CHROME_DIR):
            os.makedirs(CHROME_DIR)

        request = requests.get(self._get_system_chrome_url(), stream=True)

        with open(CHROME_ZIP_PATH, 'wb') as fd:
            for chunk in request.iter_content(chunk_size=1024):
                fd.write(chunk)

        with ZipFile(CHROME_ZIP_PATH, 'r') as zipObj:
            zipObj.extractall(CHROME_DIR)

        os.chmod(CHROME_DRIVER_PATH, 777 | stat.S_IEXEC)

    def _get_system_chrome_url(self):
        if platform == "linux" or platform == "linux2":
            return CHROME_URL_LINUX
        return CHROME_URL_MAC


class BasePageObject:
    def __init__(self, webdriver: WebDriver):
        self.webdriver = webdriver

    @property
    def messages(self):
        return [message.text for message in self.webdriver.find_elements_by_css_selector('.messages li')]

    @property
    def page_title(self):
        return self.webdriver.title

    @property
    def meta_description(self):
        return self.webdriver.find_element_by_xpath("//meta[@name='description']").get_attribute("content")
