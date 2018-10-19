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
from selenium.webdriver.firefox.options import Options


class Photographer(object):

    def __init__(self):
        self.options = Options()
        self.options.set_headless(headless=True)
        self.driver = webdriver.Firefox(
            firefox_options=self.options, log_path='/dev/null')
        self.driver.set_window_size(1920, 1080)

    def take_screenshot(self, url):
        self.driver.get(url)
        return self.driver.get_screenshot_as_base64()
