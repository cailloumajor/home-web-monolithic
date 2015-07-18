# -*- coding: utf-8 -*-

from page_objects import PageObject, PageElement, MultiPageElement

from . import JCanvasElement

class BasePage(PageObject):

    def get(self):
        super(BasePage, self).get(self.url)

    @property
    def title(self):
        return self.w.title


class HomePageSlots(BasePage):
    # Page URL
    url = '/heating/'
    # Page elements
    canvas_z1 = PageElement(id_='can-z1')
    canvas_z2 = PageElement(id_='can-z2')
    tabbtn_z2 = PageElement(xpath="//a[@href='#tab-z2']")
    legend1 = PageElement(id_='legend-add')
    legend2 = PageElement(id_='legend-E')
    legend3 = PageElement(id_='legend-H')
    legend4 = PageElement(id_='legend-A')
    del_btn = PageElement(id_='del-btn')
    slot_del_form = PageElement(id_='slot-del-form')
    slot_form = PageElement(id_='slot-form')
    day_buttons = MultiPageElement(css="#days label[role='button']")
    start_time = PageElement(id_='id_start_time')
    end_time = PageElement(id_='id_end_time')
    hours = MultiPageElement(class_name='ui-timepicker-hour-cell')
    minutes = MultiPageElement(class_name='ui-timepicker-minute-cell')
    mode_buttons = MultiPageElement(css="#mode-choices label[role='button']")
    # JCanvas elements
    slot1 = JCanvasElement(canvas_z1, 'add')
    slot2 = JCanvasElement(canvas_z1, 'pk-1')
    slot3 = JCanvasElement(canvas_z1, 'pk-2')
    slot4 = JCanvasElement(canvas_z1, 'pk-3')
    slot5 = JCanvasElement(canvas_z2, 'add')
    slot6 = JCanvasElement(canvas_z2, 'pk-4')
