# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse, resolve, NoReverseMatch

class URLTestMixin(object):

    def __init__(self, *args, **kwargs):
        self._pat_kwargs = getattr(self, 'pattern_kwargs', None)
        super(URLTestMixin, self).__init__(*args, **kwargs)

    def test_reverse_resolution(self):
        reversed_url = reverse(self.pattern_name, kwargs=self._pat_kwargs)
        self.assertEqual(reversed_url, self.expected_url)

    def test_reverse_resolution_kwargs(self):
        with self.assertRaises(NoReverseMatch):
            if self._pat_kwargs:
                reverse(self.pattern_name)
            else:
                reverse(self.pattern_name, kwargs={'test':'1'})

    def test_url_view_resolve(self):
        viewname = resolve(self.expected_url).func.__name__
        self.assertEqual(viewname, self.expected_view)

class ZoneListURLTests(URLTestMixin, TestCase):
    pattern_name = 'zone_list'
    expected_url = '/heating/'
    expected_view = 'ZoneList'

class SlotCreateURLTests(URLTestMixin, TestCase):
    pattern_name = 'new_slot'
    pattern_kwargs = {'zone': '2'}
    expected_url = '/heating/slot/new/zone_2/'
    expected_view = 'SlotCreate'

class SlotUpdateURLTests(URLTestMixin, TestCase):
    pattern_name = 'update_slot'
    pattern_kwargs = {'pk': '3'}
    expected_url = '/heating/slot/3/'
    expected_view = 'SlotUpdate'

class SlotDeleteURLTests(URLTestMixin, TestCase):
    pattern_name = 'del_slot'
    pattern_kwargs = {'pk': '4'}
    expected_url = '/heating/slot/4/delete/'
    expected_view = 'SlotDelete'
