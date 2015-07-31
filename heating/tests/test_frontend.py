# -*- coding: utf-8 -*-

import os
from datetime import timedelta

from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from django_dynamic_fixture import G, F

from .frontend import pages, FrontendTestCase, JCanvasElementNotFound
from ..models import Derogation


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

    def setUp(self):
        now = timezone.now()
        # Past derogation
        G(Derogation, mode='E', zones=[F(num=1)],
          creation_dt=now-timedelta(days=1, hours=2),
          end_dt=now-timedelta(hours=1))
        # Active derogation
        G(Derogation, mode='H', zones=[F(num=2)],
          creation_dt=now-timedelta(days=1, hours=1),
          start_dt=now-timedelta(hours=1),
          end_dt=now+timedelta(hours=1))
        # Future derogation
        G(Derogation, mode='A', zones=[F(num=3)],
          creation_dt=now-timedelta(days=1),
          start_dt=now+timedelta(hours=1),
          end_dt=now+timedelta(hours=2))
        super(HomePageTestDerogations, self).setUp()
        self.wait = WebDriverWait(self.driver, 2, 0.1)

    def test_title(self):
        self.assertRegex(self.page.header.text, r'^Dérogations')

    def test_no_derogation(self):
        Derogation.objects.all().delete()
        self.refresh_derogations()
        colspan = self.page.no_derog_cell.get_attribute('colspan')
        self.assertEqual(int(colspan), len(self.page.derog_head_cells))

    def test_mode_colors(self):
        self.assertColorAlmostEqual(
            self.page.columns(self.page.rows[0])[4].color,
            self.page.legend[1].color)
        self.assertColorAlmostEqual(
            self.page.columns(self.page.rows[1])[4].color,
            self.page.legend[2].color)
        self.assertColorAlmostEqual(
            self.page.columns(self.page.rows[2])[4].color,
            self.page.legend[3].color)

    def test_past_derogation(self):
        opacity = float(self.page.rows[0].value_of_css_property('opacity'))
        self.assertLess(opacity, 1.0)
        self.assertEqual(self.page.columns(self.page.rows[0])[0].text, '')

    def test_active_derogation(self):
        opacity = float(self.page.rows[1].value_of_css_property('opacity'))
        self.assertEqual(opacity, 1.0)
        self.assertEqual(self.page.columns(self.page.rows[1])[0].text, 'X')

    def test_future_derogation(self):
        opacity = float(self.page.rows[2].value_of_css_property('opacity'))
        self.assertEqual(opacity, 1.0)
        self.assertEqual(self.page.columns(self.page.rows[2])[0].text, '')

    def test_zone_1(self):
        self.assertEqual(self.page.columns(self.page.rows[0])[5].text, 'X')
        self.assertEqual(self.page.columns(self.page.rows[0])[6].text, '')
        self.assertEqual(self.page.columns(self.page.rows[0])[7].text, '')

    def test_zone_2(self):
        self.assertEqual(self.page.columns(self.page.rows[1])[5].text, '')
        self.assertEqual(self.page.columns(self.page.rows[1])[6].text, 'X')
        self.assertEqual(self.page.columns(self.page.rows[1])[7].text, '')

    def test_zone_3(self):
        self.assertEqual(self.page.columns(self.page.rows[2])[5].text, '')
        self.assertEqual(self.page.columns(self.page.rows[2])[6].text, '')
        self.assertEqual(self.page.columns(self.page.rows[2])[7].text, 'X')

    def test_derogation_deletion(self):
        self.assertEqual(len(self.page.rows), 3)
        self.page.del_btn(self.page.rows[0]).click()
        self.page.del_form.submit()
        self.wait.until(
            EC.invisibility_of_element_located((By.ID, 'derogation-del-form')))
        self.assertEqual(len(self.page.rows), 2)

    def test_derogation_creation(self):
        self.assertEqual(len(self.page.rows), 3)
        self.page.add_btn.click()
        self.page.zones_multiselect.click()
        for chk in self.page.zones_checkboxes:
            chk.click()
        self.page.start_dt.click()
        self.wait.until(EC.visibility_of(self.page.start_dtpicker))
        self.page.next_month(self.page.start_dtpicker).click()
        self.page.days(self.page.start_dtpicker)[1].click()
        self.page.times(self.page.start_dtpicker)[1].click()
        self.page.start_dt.click()
        self.page.end_dt.click()
        self.wait.until(EC.visibility_of(self.page.end_dtpicker))
        self.page.next_month(self.page.end_dtpicker).click()
        self.page.days(self.page.end_dtpicker)[2].click()
        self.page.times(self.page.end_dtpicker)[2].click()
        self.page.end_dt.click()
        self.page.mode_buttons[1].click()
        self.page.add_form.submit()
        self.wait.until(
            EC.invisibility_of_element_located((By.ID, 'derogation-form')))
        self.assertEqual(len(self.page.rows), 4)
