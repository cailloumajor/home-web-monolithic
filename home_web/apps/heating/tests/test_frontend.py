# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from xvfbwrapper import Xvfb

from .frontend import pages


def setUpModule():
    global xserver
    global driver
    xserver = Xvfb(width=1360, height=768, nolisten='tcp')
    xserver.start()
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.implicitly_wait(2)

def tearDownModule():
    driver.quit()
    xserver.stop()


class FrontendTestCase(StaticLiveServerTestCase):

    def setUp(self):
        super(FrontendTestCase, self).setUp()
        driver.root_uri = self.live_server_url
        self.page = self.page_class(driver)
        self.page.get()


class HomePageTest(FrontendTestCase):
    page_class = pages.HomePage

    def test_title(self):
        self.assertEqual(self.page.title, 'Gestion du chauffage')
