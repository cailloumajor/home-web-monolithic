# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.utils import timezone

from django_dynamic_fixture import G, N, F

from ..models import Zone, Slot, Derogation

class ZoneModelTest(TestCase):

    def test_string_representation(self):
        zone = N(Zone)
        self.assertEqual(str(zone), 'Z{}'.format(zone.num))

    def test_get_modes_queryset_method(self):
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
            end_dt = timezone.now() + datetime.timedelta(minutes=2),
        )
        self.assertEqual(Zone.objects.get_modes(), {'1':'C','2':'E','3':'A'})

class SlotModelTest(TestCase):

    def test_string_representation(self):
        slot = N(
            Slot, mon=True, wed=True, fri=True, sun=True, mode = 'E',
            start_time = datetime.time(4, 2), end_time = datetime.time(15, 54)
        )
        self.assertEqual(
            str(slot), "Z{} 04:02:00-15:54:00 [L*M*V*D] Eco".format(slot.zone.num)
        )

    def test_is_active_queryset_method(self):
        zone = G(Zone, num=1)
        wdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        now = timezone.localtime(timezone.now())
        if now.time().hour < 1:
            raise Exception("This test cannot be run between 00:00 and 01:00")
        kwargs = {
            'zone': zone, wdays[now.weekday()]: True, 'mode': 'E',
            'start_time': (now - datetime.timedelta(hours=1)).time(),
            'end_time': (now - datetime.timedelta(minutes=2)).time()
        }
        past_slot = G(Slot, **kwargs)
        kwargs = {
            'zone': zone, wdays[now.weekday()]: True, 'mode': 'E',
            'start_time': now.time(),
            'end_time': (now + datetime.timedelta(minutes=2)).time()
        }
        active_slot = G(Slot, **kwargs)
        kwargs = {
            'zone': zone, wdays[now.weekday()]: True, 'mode': 'E',
            'start_time': (now + datetime.timedelta(minutes=2)).time(),
            'end_time': (now - datetime.timedelta(hours=1)).time()
        }
        future_slot = G(Slot, **kwargs)
        kwargs = {
            'zone': zone, wdays[(now.weekday() - 1) % 7]: True, 'mode': 'E',
            'start_time': (now - datetime.timedelta(hours=1)).time(),
            'end_time': (now - datetime.timedelta(minutes=2)).time()
        }
        yesterday_slot = G(Slot, **kwargs)
        kwargs = {
            'zone': zone, wdays[(now.weekday() + 1) % 7]: True, 'mode': 'E',
            'start_time': (now - datetime.timedelta(hours=1)).time(),
            'end_time': (now - datetime.timedelta(minutes=2)).time()
        }
        tomorrow_slot = G(Slot, **kwargs)
        queryset = Slot.objects.is_active()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0], active_slot)

class DerogationModelTest(TestCase):

    def create_entries_for_active_tests(self):
        self.past_derog = G(
            Derogation, mode = 'E',
            start_dt = timezone.now() - datetime.timedelta(days=1),
            end_dt = timezone.now() - datetime.timedelta(minutes=2)
        )
        self.active_derog = G(
            Derogation, mode = 'E',
            start_dt = timezone.now(),
            end_dt = timezone.now() + datetime.timedelta(minutes=2)
        )
        self.future_derog = G(
            Derogation, mode = 'E',
            start_dt = timezone.now() + datetime.timedelta(minutes=2),
            end_dt = timezone.now() + datetime.timedelta(days=1)
        )

    def test_string_representation(self):
        tz = timezone.get_default_timezone()
        start = timezone.make_aware(
            datetime.datetime(2015, 2, 25, 17, 24), tz
        )
        end = timezone.make_aware(
            datetime.datetime(2015, 3, 18, 18, 12), tz
        )
        derog = G(Derogation, start_dt=start, end_dt=end, mode='H',
                  zones=[F(num=2), F(num=3)])
        self.assertEqual(str(derog), "25/02-17:24->18/03-18:12 H Z2-Z3")

    def test_is_active_queryset_method(self):
        self.create_entries_for_active_tests()
        queryset = Derogation.objects.is_active()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0], self.active_derog)

    def test_active_model_method(self):
        self.create_entries_for_active_tests()
        self.assertFalse(self.past_derog.active())
        self.assertTrue(self.active_derog.active())
        self.assertFalse(self.future_derog.active())

    def test_is_outdated_queryset_method(self):
        self.create_entries_for_active_tests()
        queryset = Derogation.objects.is_outdated()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0], self.past_derog)

    def test_outdated_model_method(self):
        self.create_entries_for_active_tests()
        self.assertTrue(self.past_derog.outdated())
        self.assertFalse(self.active_derog.outdated())
        self.assertFalse(self.future_derog.outdated())
