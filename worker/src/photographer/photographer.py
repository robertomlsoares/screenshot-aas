# coding: utf-8

"""
    photographer
    ~~~~~~~~~~~~

    The class responsible for using Selenium to take screenshots of websites.

    :copyright: (c) 2018 Roberto Soares
    :license: GPL-3.0
"""

import hashlib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Photographer(object):

    def __init__(self):
        self.options = Options()
        self.options.set_headless(headless=True)
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-extensions')
        self.driver = webdriver.Chrome(
            chrome_options=self.options, service_log_path='/dev/null')
        self.driver.set_window_size(1920, 1080)

    def take_screenshot(self, url):
        self.driver.get(url)
        img = self.driver.get_screenshot_as_base64()
        self.driver.quit()
        return img
