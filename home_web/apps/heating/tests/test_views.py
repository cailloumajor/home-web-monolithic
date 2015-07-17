# -*- coding: utf-8 -*-

import datetime
import json
import random
import locale

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from django_dynamic_fixture import G, F

from ..models import Zone, Slot, Derogation

class ZoneViewsTest(TestCase):

    def test_zone_list_view(self):
        hmtime = lambda t: t.strftime('%H:%M')
        s1 = G(Slot, mode='E', zone=F(num=1))
        s2 = G(Slot, mode='H', zone=F(num=2))
        response = self.client.get(reverse('zone_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Zone {}".format(s1.zone.num))
        self.assertContains(response, "Zone {}".format(s2.zone.num))
        self.assertContains(response, s1.zone.desc)
        self.assertContains(response, s2.zone.desc)
        self.assertContains(response, hmtime(s1.start_time))
        self.assertContains(response, hmtime(s1.end_time))
        self.assertContains(response, hmtime(s2.start_time))
        self.assertContains(response, hmtime(s2.end_time))

    def test_derogation_in_zone_list_view(self):
        locale.setlocale(locale.LC_ALL, '')
        strdt = lambda dt: timezone.localtime(dt).strftime("%d %B %Y %H:%M")
        derog = G(Derogation, mode = 'A')
        response = self.client.get(reverse('zone_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, strdt(derog.creation_dt))
        self.assertContains(response, strdt(derog.start_dt))
        self.assertContains(response, strdt(derog.end_dt))
        self.assertContains(response, derog.get_mode_display())

class SlotViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls._zone = G(Zone)
        cls._slot = G(Slot, zone=cls._zone, mode='A')
            
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
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict, response_non_ajax.context['form'].errors)

    def test_ajax_slot_create_view_form_valid(self):
        z = G(Zone)
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
        created_slot = Slot.objects.all()[0]
        model_dict = model_to_dict(created_slot)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(response_dict, dict)
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
        s = G(Slot, mon=True, mode='E')
        self.assertEqual(Slot.objects.all().get(), s)
        response = self.client.post(reverse('del_slot', kwargs={'pk':s.pk}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict.get('django_success'),
                         True)

class ModeAPIViewTest(TestCase):

    def test_mode_api_view(self):
        wdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        now = timezone.localtime(timezone.now())
        z1 = G(Zone, num=1)
        kwargs = {
            'zone': F(num=2), wdays[now.weekday()]: True, 'mode': 'E',
            'start_time': (now - datetime.timedelta(minutes=2)).time(),
            'end_time': (now + datetime.timedelta(minutes=2)).time(),
        }
        slot_z2 = G(Slot, **kwargs)
        kwargs = {
            'zone': F(num=3), wdays[now.weekday()]: True, 'mode': 'H',
            'start_time': (now - datetime.timedelta(minutes=2)).time(),
            'end_time': (now + datetime.timedelta(minutes=2)).time(),
        }
        slot_z3 = G(Slot, **kwargs)
        derog_z3 = G(
            Derogation, mode = 'A', zones=[F(num=3)],
            start_dt = timezone.now() - datetime.timedelta(minutes=2),
            end_dt = timezone.now() + datetime.timedelta(minutes=2)
        )
        response = self.client.get(reverse('api_mode'))
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict, {'modes':{'1':'C','2':'E','3':'A'}})

class DerogationViewsTest(TestCase):

    def test_derogation_create_view(self):
        response = self.client.get(reverse('new_derog'))
        self.assertEqual(response.status_code, 200)

    def test_derogation_list_view(self):
        response = self.client.get(reverse('derog_list'))
        self.assertEqual(response.status_code, 200)

    def test_derogation_delete_view(self):
        derog = G(Derogation, mode='E')
        response = self.client.get(reverse('del_derog', kwargs={'pk':derog.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(derog).replace('>', '&gt;'))
