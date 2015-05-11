# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.color import Color
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import Remote


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
            """
            return (function() {{
                var group = $('#{canvas_id}').getLayerGroup('{group_name}');
                if (group === undefined) {{
                    return 'LayerGroupNotFound';
                }}
                var lst = [];
                for (var i = 0 ; i < group.length ; i++) {{
                    var prop = group[i]['{prop}'];
                    if (prop === undefined) {{
                        return 'PropertyNotFound';
                    }}
                    lst.push(prop);
                }}
                return lst;
            }})();
            """.format(canvas_id=self._canvas_id,
                       group_name=self._group_name,
                       prop=name)
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
            """
            var canvas = document.getElementById('{can_id}');
            var ctx = canvas.getContext('2d');
            return ctx.getImageData({x}, {y}, 1, 1).data;
            """.format(
                can_id = self._canvas_id,
                x = self.x[0] + 5,
                y = self.y[0] + 5,
            )
        )
        alpha = rgba[3] / 255.0
        rgb = [int(round((comp / 255.0 * alpha + 1 - alpha) * 255.0))
               for comp in rgba[:3]]
        return 'rgb({},{},{})'.format(*rgb)

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

    fixtures = ['test_frontend.json']

    def setUp(self):
        super(FrontendTestCase, self).setUp()
        self.driver.root_uri = self.live_server_url
        self.page = self.page_class(self.driver)
        self.page.get()
        wait = WebDriverWait(self.driver, 5)
        el = wait.until(EC.visibility_of_element_located(self.ready_locator))
        if type(self.driver) is Remote:
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
            self.driver.execute_script(script)

    def tearDown(self):
        if type(self.driver) is Remote:
            self.driver.execute_script(
                ("$('#test-id').css('background-color', 'red')"
                 ".append(' >> CLICK FOR NEXT TEST <<');")
            )
            wait = WebDriverWait(self.driver, 300)
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
