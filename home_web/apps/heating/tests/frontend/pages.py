# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from page_objects import PageObject, PageElement

class BasePage(PageObject):

    def get(self):
        super(BasePage, self).get(self.url)

    @property
    def title(self):
        return self.w.title


class HomePage(BasePage):
    url = '/heating/'
    canvas_z1 = PageElement(id_='can-z1')
    canvas_z2 = PageElement(id_='can-z2')
    tabbtn_z2 = PageElement(xpath="//a[@href='#tab-z2']")
    legend1 = PageElement(id_='legend-add')
    legend2 = PageElement(id_='legend-E')
    legend3 = PageElement(id_='legend-H')
    legend4 = PageElement(id_='legend-A')
    del_btn = PageElement(id_='del-btn')
    slot_del_form = PageElement(id_='slot-del-form')
