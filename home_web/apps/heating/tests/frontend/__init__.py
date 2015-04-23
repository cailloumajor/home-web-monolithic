# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class JCanvasElementNotFound(Exception):

    def __init__(self, can_id, group_name):
        message = (
            "JCanvas object not found "
            "- id: '{}' - groupName: '{}'".format(can_id, group_name)
        )
        super(JCanvasElementNotFound, self).__init__(message)


class JCanvasElement(object):
    """JCanvas layer group representation.

    :param canvas: `page_objects.PageElement`
        The canvas element containing this JCanvas layer group
    :param groupName: `str`
        The name of the JCanvas layer group
    """

    def __init__(self, canvas, groupName):
        self._canvas = canvas
        self._canvas_id = canvas.get_attribute('id')
        self._driver = canvas.parent
        self._group_name = groupName

    def __getattr__(self, name):
        if name in self._layer_group[0]:
            return [layer[name] for layer in self._layer_group]
        else:
            raise AttributeError(name)

    @property
    def _layer_group(self):
        group = self._driver.execute_script(
            "return $('#{}').getLayerGroup('{}')".format(
                self._canvas_id, self._group_name
            )
        )
        if not isinstance(group, list):
            raise JCanvasElementNotFound(self._canvas_id, self._group_name)
        return group

    @property
    def count(self):
        return len(self._layer_group)

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
