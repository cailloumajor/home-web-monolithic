# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from page_objects import PageObject, PageElement

class BasePage(PageObject):

    def get(self):
        super(BasePage, self).get(self.url)

    @property
    def title(self):
        return self.w.title
