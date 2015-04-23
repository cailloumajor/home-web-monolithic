# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.color import Color
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from xvfbwrapper import Xvfb

from .frontend import pages, JCanvasElement


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

    def assertAreSameColor(self, first, second, msg=None):
        def get_color(element):
            if isinstance(element, WebElement):
                color_rgba = element.value_of_css_property('background-color')
            elif isinstance(element, JCanvasElement):
                color_rgba = element.color
            else:
                raise TypeError(
                    "bad element type '{}'".format(type(element).__name__)
                )
            return Color.from_string(color_rgba)
        colors = [get_color(element) for element in [first, second]]
        self.assertEqual(*colors, msg=msg)


class HomePageTest(FrontendTestCase):

    page_class = pages.HomePage
    ready_locator = (By.CLASS_NAME, 'show-if-js')

    def setUp(self):
        super(HomePageTest, self).setUp()
        self.slot1 = JCanvasElement(self.page.canvas_z1, 'add')
        self.slot2 = JCanvasElement(self.page.canvas_z1, 'pk-1')
        self.slot3 = JCanvasElement(self.page.canvas_z1, 'pk-2')
        self.slot4 = JCanvasElement(self.page.canvas_z1, 'pk-3')

    def test_title(self):
        self.assertEqual(self.page.title, 'Gestion du chauffage')

    def test_tab_content_visibility(self):
        self.assertTrue(self.page.canvas_z1.is_displayed())
        self.assertFalse(self.page.canvas_z2.is_displayed())
        self.page.tabbtn_z2.click()
        self.assertFalse(self.page.canvas_z1.is_displayed())
        self.assertTrue(self.page.canvas_z2.is_displayed())

    def test_slot_color_against_legend(self):
        self.assertAreSameColor(self.slot1, self.page.legend1)
        self.assertAreSameColor(self.slot2, self.page.legend2)
        self.assertAreSameColor(self.slot3, self.page.legend3)
        self.assertAreSameColor(self.slot4, self.page.legend4)

    def test_slots_number_in_group(self):
        self.assertEqual(self.slot1.count, 7)
        self.assertEqual(self.slot2.count, 4)
        self.assertEqual(self.slot3.count, 3)
        self.assertEqual(self.slot4.count, 1)
