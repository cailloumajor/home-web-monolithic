# -*- coding: utf-8 -*-

import datetime
import random

from django.test import TestCase
from django.core.urlresolvers import reverse

from ..models import Zone, Slot

def create_slot(zone, mode):
    st = datetime.time(random.randint(0,23), random.randint(0,59))
    et = datetime.time(random.randint(0,23), random.randint(0,59))
    return Slot.objects.create(zone=zone, mode=mode, start_time=st, end_time=et)

class ZoneViewsTest(TestCase):

    def test_zone_list_view(self):
        hmtime = lambda t: t.strftime('%H:%M')
        z1 = Zone.objects.create(num=1, desc="Zone test 1")
        z2 = Zone.objects.create(num=2, desc="Zone test 2")
        s1 = create_slot(z1, 'H')
        s2 = create_slot(z2, 'A')
        response = self.client.get(reverse('zone_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Zone {}".format(z1.num))
        self.assertContains(response, "Zone {}".format(z2.num))
        self.assertContains(response, z1.desc)
        self.assertContains(response, z2.desc)
        self.assertContains(response, hmtime(s1.start_time))
        self.assertContains(response, hmtime(s1.end_time))
        self.assertContains(response, hmtime(s2.start_time))
        self.assertContains(response, hmtime(s2.end_time))

class SlotViewsTest(TestCase):

    def setUp(self):
        self._zone = Zone.objects.create(num=1, desc="Zone test")
        self._slot = create_slot(self._zone, 'E')
            
    def test_slot_create_view(self):
        response = self.client.get(reverse('new_slot', kwargs={'zone':self._zone.num}))
        self.assertEqual(response.status_code, 200)

    def test_slot_update_view(self):
        response = self.client.get(reverse('update_slot', kwargs={'pk':self._slot.pk}))
        self.assertEqual(response.status_code, 200)

    def test_slot_delete_view(self):
        response = self.client.get(reverse('del_slot', kwargs={'pk':self._slot.pk}))
        self.assertEqual(response.status_code, 200)
