# -*- coding: utf-8 -*-

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.color import Color
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import Remote

from .jsscripts import external_javascript as js


class JCanvasElementBaseException(Exception):

    def __init__(self, instance):
        message = (
            self.reason +
            " - id: '{}' - groupName: '{}'".format(
                instance._canvas_id, instance._group_name
            )
        )
        super(JCanvasElementBaseException, self).__init__(message)


class JCanvasElementNotFound(JCanvasElementBaseException):
    reason = "JCanvas element not found"


class JCanvasElementNotVisible(JCanvasElementBaseException):
    reason = "Could not interact with JCanvas element, canvas is not visible"


class JCanvasElementContainer(object):
    """JCanvas layer group representation.

    :param canvas: `page_objects.PageElement`
        The canvas element containing this JCanvas layer group
    :param groupName: `str`
        The name of the JCanvas layer group
    """

    def __init__(self, canvas, driver, groupName):
        self._canvas = canvas
        self._canvas_id = canvas.get_attribute('id')
        self._driver = driver
        self._group_name = groupName

    def __getattr__(self, name):
        result = self._driver.execute_script(
            js.get_script('get_layer_group_property'),
            self._canvas_id, self._group_name, name
        )
        if (result == 'LayerGroupNotFound'):
            raise JCanvasElementNotFound(self)
        elif (result == 'PropertyNotFound'):
            raise AttributeError(name)
        else:
            return result

    @property
    def count(self):
        return len(self.index)

    @property
    def color(self):
        rgba = self._driver.execute_script(
            js.get_script('get_color_on_canvas'),
            self._canvas_id, self.x[0] + 5, self.y[0] + 5
        )
        alpha = rgba[3]
        rgb = [int(round(255 - alpha + alpha * comp / 255.0))
               for comp in rgba[:3]]
        return Color(*rgb)

    def click(self):
        if not self._canvas.is_displayed():
            raise JCanvasElementNotVisible(self)
        action = ActionChains(self._driver)
        action.move_to_element_with_offset(
            self._canvas,
            int(self.x[0]) + 5,
            int(self.y[0]) + 5
        )
        action.click().perform()


class JCanvasElement(object):

    def __init__(self, canvas_element, groupName):
        self._canvas_element = canvas_element
        self._group_name = groupName

    def __get__(self, instance, owner):
        if not instance:
            return None
        return JCanvasElementContainer(
            instance.w.find_element(*self._canvas_element.locator),
            instance.w,
            self._group_name
        )


class FrontendTestCase(StaticLiveServerTestCase):

    def __init__(self, *args, **kwargs):
        super(FrontendTestCase, self).__init__(*args, **kwargs)
        self.addTypeEqualityFunc(Color, 'assertColorAlmostEqual')

    def setUp(self):
        super(FrontendTestCase, self).setUp()
        self.driver.root_uri = self.live_server_url
        self.page = self.page_class(self.driver)
        self.page.get()
        wait = WebDriverWait(self.driver, 5)
        el = wait.until(EC.visibility_of_element_located(self.ready_locator))
        if type(self.driver) is Remote:
            self.driver.execute_script(
                js.get_script('create_test_info_element'),
                self.id()
            )
            wait = WebDriverWait(self.driver, 300)
            el = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'start-test'))
            )

    def tearDown(self):
        if type(self.driver) is Remote:
            self.driver.execute_script(
                js.get_script('click_for_next_test')
            )
            wait = WebDriverWait(self.driver, 300)
            el = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'next-test'))
            )
        super(FrontendTestCase, self).tearDown()

    def assertColorAlmostEqual(self, color1, color2, msg=None):
        standardMsg = "Colors differ: {} != {}".format(color1, color2)
        msg = self._formatMessage(msg, standardMsg)
        if color1 == color2:
            return
        if not round(abs(float(color1.alpha) - float(color2.alpha)), 2) == 0:
            self.fail(msg)
        for comp in ('red', 'green', 'blue'):
            comp_color1 = getattr(color1, comp)
            comp_color2 = getattr(color2, comp)
            if abs(comp_color1 - comp_color2) > 2:
                self.fail(msg)

    def refresh_derogations(self):
        self.driver.execute_script(js.get_script('refresh_derogations'))
        wait = WebDriverWait(self.driver, 5)
        el = wait.until(
            EC.presence_of_element_located((By.ID, 'derogation-table')))


def get_webelement_color(self):
    return Color.from_string(self.value_of_css_property('background-color'))

WebElement.color = property(get_webelement_color)
