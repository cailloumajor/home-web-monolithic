# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.color import Color
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from xvfbwrapper import Xvfb

from .frontend import pages, JCanvasElementContainer, JCanvasElementNotFound


def setUpModule():
    global xserver
    global driver
    xserver = Xvfb(width=1360, height=768, nolisten='tcp')
    remote_host = os.environ.get('REMOTE_WD')
    if remote_host is None:
        xserver.start()
        driver = webdriver.Firefox()
    else:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((remote_host, 4444))
        os.environ.setdefault('DJANGO_LIVE_TEST_SERVER_ADDRESS',
                              '{}:8081'.format(s.getsockname()[0]))
        s.close()
        driver = webdriver.Remote('http://{}:4444/wd/hub'.format(remote_host),
                                  webdriver.DesiredCapabilities.FIREFOX.copy())
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
        if type(driver) is webdriver.Remote:
            driver.root_uri = 'http://192.168.1.20:8081'
            script = (
                """
                $('body').css('position', 'relative');
                $('<div>', {{
                    'id': 'test-id',
                    text: '{test_info}',
                    css: {{
                        'background-color': 'yellow',
                        'position': 'absolute',
                        'top': '0', 'right': '0',
                        'cursor': 'pointer',
                    }},
                    click: function() {{
                        $(this).attr('id', 'next-test');
                    }},
                }}).appendTo('body');
                """.format(test_info=self.id())
            )
            driver.execute_script(script)

    def tearDown(self):
        if type(driver) is webdriver.Remote:
            driver.execute_script(
                ("$('#test-id').css('background-color', 'red')"
                 ".append(' >> CLICK FOR NEXT TEST <<');")
            )
            wait = WebDriverWait(driver, 300)
            el = wait.until(
                EC.presence_of_element_located((By.ID, 'next-test'))
            )
        super(FrontendTestCase, self).tearDown()

    def assertAreSameColor(self, first, second, msg=None):
        def get_color(element):
            if isinstance(element, WebElement):
                color_rgba = element.value_of_css_property('background-color')
            elif isinstance(element, JCanvasElementContainer):
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

    def test_title(self):
        self.assertEqual(self.page.title, 'Gestion du chauffage')

    def test_tab_content_visibility(self):
        self.assertTrue(self.page.canvas_z1.is_displayed())
        self.assertFalse(self.page.canvas_z2.is_displayed())
        self.page.tabbtn_z2.click()
        self.assertFalse(self.page.canvas_z1.is_displayed())
        self.assertTrue(self.page.canvas_z2.is_displayed())

    def test_slot_color_against_legend(self):
        self.assertAreSameColor(self.page.slot1, self.page.legend1)
        self.assertAreSameColor(self.page.slot2, self.page.legend2)
        self.assertAreSameColor(self.page.slot3, self.page.legend3)
        self.assertAreSameColor(self.page.slot4, self.page.legend4)

    def test_slots_number_in_group(self):
        self.assertEqual(self.page.slot1.count, 7)
        self.assertEqual(self.page.slot2.count, 4)
        self.assertEqual(self.page.slot3.count, 3)
        self.assertEqual(self.page.slot4.count, 1)

    def test_slot_deletion(self):
        self.page.del_btn.click()
        self.page.slot2.click()
        self.page.slot_del_form.submit()
        with self.assertRaises(JCanvasElementNotFound):
            c = self.page.slot2.count
