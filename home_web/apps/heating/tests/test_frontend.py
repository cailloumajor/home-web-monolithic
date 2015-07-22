# -*- coding: utf-8 -*-

import os

from selenium import webdriver
from selenium.webdriver.common.by import By

from .frontend import pages, FrontendTestCase, JCanvasElementNotFound


def setUpModule():
    global driver
    remote_host = os.environ.get('REMOTE_WD')
    if remote_host is None:
        driver = webdriver.PhantomJS(service_args=['--debug=true'])
    else:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((remote_host, 4444))
        os.environ.setdefault('DJANGO_LIVE_TEST_SERVER_ADDRESS',
                              '{}:8081'.format(s.getsockname()[0]))
        s.close()
        driver = webdriver.Remote('http://{}:4444/wd/hub'.format(remote_host),
                                  webdriver.DesiredCapabilities.FIREFOX.copy())
    FrontendTestCase.driver = driver
    driver.maximize_window()
    driver.implicitly_wait(2)

def tearDownModule():
    driver.quit()


class HomePageTestSlots(FrontendTestCase):

    fixtures = ['test_slots_frontend.json']
    page_class = pages.HomePageSlots
    ready_locator = (By.CLASS_NAME, 'show-if-js-done')

    def test_title(self):
        self.assertEqual(self.page.title, 'Gestion du chauffage')

    def test_tab_content_visibility(self):
        self.assertTrue(self.page.canvas_z1.is_displayed())
        self.assertFalse(self.page.canvas_z2.is_displayed())
        self.page.tabbtn_z2.click()
        self.assertFalse(self.page.canvas_z1.is_displayed())
        self.assertTrue(self.page.canvas_z2.is_displayed())

    def test_slot_color_against_legend(self):
        self.assertEqual(self.page.slot1.color, self.page.legend1.color)
        self.assertEqual(self.page.slot2.color, self.page.legend2.color)
        self.assertEqual(self.page.slot3.color, self.page.legend3.color)
        self.assertEqual(self.page.slot4.color, self.page.legend4.color)

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

    def test_slot_adding(self):
        self.page.tabbtn_z2.click()
        self.page.slot5.click()
        self.page.day_buttons[1].click()
        self.page.day_buttons[4].click()
        self.page.start_time.click()
        self.page.hours[6].click()
        self.page.minutes[1].click()
        self.page.end_time.click()
        self.page.hours[14].click()
        self.page.minutes[3].click()
        self.page.mode_buttons[2].click()
        self.page.slot_form.submit()
        self.assertEqual(self.page.slot6.width, [340, 340])
        self.assertEqual(self.page.slot6.x, [290.5, 290.5])
        self.assertEqual(self.page.slot6.y, [57.5, 147.5])

    def test_slot_modification(self):
        self.page.slot4.click()
        self.page.day_buttons[4].click()
        self.page.end_time.click()
        self.page.hours[19].click()
        self.page.minutes[0].click()
        self.page.mode_buttons[0].click()
        self.page.slot_form.submit()
        self.assertEqual(self.page.slot4.width, [120, 120])
        self.assertEqual(self.page.slot4.color, self.page.legend2.color)


class HomePageTestDerogations(FrontendTestCase):

    page_class = pages.HomePageDerogations
    ready_locator = (By.CLASS_NAME, 'show-if-js-done')

    def test_title(self):
        self.assertRegex(self.page.header.text, r'^Dérogations')
