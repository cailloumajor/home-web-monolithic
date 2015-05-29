# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json
import random

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

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
        response = self.client.get(
            reverse('new_slot', kwargs={'zone':self._zone.num})
        )
        self.assertEqual(response.status_code, 200)

    def test_slot_update_view(self):
        response = self.client.get(
            reverse('update_slot', kwargs={'pk':self._slot.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_slot_delete_view(self):
        response = self.client.get(
            reverse('del_slot', kwargs={'pk':self._slot.pk})
        )
        self.assertEqual(response.status_code, 200)

class AjaxSlotViewsTest(TestCase):

    longMessage = True

    def test_ajax_slot_create_view_form_invalid(self):
        url = reverse('new_slot', kwargs={'zone':1})
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_non_ajax = self.client.post(url)
        self.assertIsInstance(json.loads(response.content), dict)
        self.assertEqual(json.loads(response.content),
                         response_non_ajax.context['form'].errors)

    def test_ajax_slot_create_view_form_valid(self):
        z = Zone.objects.create(num=1, desc="Test zone")
        response = self.client.post(
            reverse('new_slot', kwargs={'zone':z.num}),
            {
                'zone': z.num, 'mon': True,
                'start_time': '04:30',
                'end_time': '06:30',
                'mode': 'E'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertIsInstance(json.loads(response.content), dict)
        created_slot = Slot.objects.all()[0]
        model_dict = model_to_dict(created_slot)
        response_dict = json.loads(response.content)
        for key in model_dict:
            self.assertEqual(
                response_dict.get(key),
                json.loads(json.dumps(model_dict[key], cls=DjangoJSONEncoder)),
                msg="Field: {}".format(key)
            )
        self.assertEqual(response_dict.get('django_success'),
                         True)
        self.assertEqual(response_dict.get('pk'),
                         'pk-{}'.format(created_slot.pk))
        self.assertEqual(response_dict.get('addUpdURL'),
                         reverse('update_slot', kwargs={'pk':created_slot.pk}))
        self.assertEqual(response_dict.get('delURL'),
                         reverse('del_slot', kwargs={'pk':created_slot.pk}))

    def test_ajax_slot_delete_view(self):
        z = Zone.objects.create(num=1, desc="Test zone")
        s = Slot.objects.create(
            zone=z, mon=True, mode='E',
            start_time=datetime.time(4), end_time=datetime.time(6),
        )
        self.assertEqual(Slot.objects.all().get(), s)
        response = self.client.post(reverse('del_slot', kwargs={'pk':s.pk}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertIsInstance(json.loads(response.content), dict)
        self.assertEqual(json.loads(response.content).get('django_success'),
                         True)
