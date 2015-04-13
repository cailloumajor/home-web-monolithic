# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

    fixtures = ['test_frontend.json']

    def setUp(self):
        super(FrontendTestCase, self).setUp()
        driver.root_uri = self.live_server_url
        self.page = self.page_class(driver)
        self.page.get()
        wait = WebDriverWait(driver, 5)
        el = wait.until(EC.visibility_of_element_located(self.ready_locator))


class HomePageTest(FrontendTestCase):

    page_class = pages.HomePage
    ready_locator = (By.CLASS_NAME, 'show-if-js')

    def test_title(self):
        self.assertEqual(self.page.title, 'Gestion du chauffage')

    def test_tab_content_visibility(self):
        self.assertTrue(self.page.canvas_z1.is_displayed())
        self.assertFalse(self.page.canvas_z2.is_displayed())
        self.page.tabbtn_z2.click()
        self.assertFalse(self.page.canvas_z1.is_displayed())
        self.assertTrue(self.page.canvas_z2.is_displayed())
