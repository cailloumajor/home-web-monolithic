# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.utils import timezone

from ..models import Zone, Slot, Derogation

class ZoneModelTest(TestCase):

    def test_string_representation(self):
        zone = Zone(num=1)
        self.assertEqual(str(zone), 'Z{}'.format(zone.num))

    def test_is_active_queryset_method(self):
        zone = Zone(num=1)
        wdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        now = timezone.localtime(timezone.now())
        if now.time().hour < 1:
            raise Exception("This test cannot be run between 00:00 and 01:00")
        z1 = Zone.objects.create(num=1)
        z2 = Zone.objects.create(num=2)
        z3 = Zone.objects.create(num=3)
        kwargs = {
            'zone': z2, wdays[now.weekday()]: True, 'mode': 'E',
            'start_time': (now - datetime.timedelta(minutes=2)).time(),
            'end_time': (now + datetime.timedelta(minutes=2)).time(),
        }
        slot_z2 = Slot.objects.create(**kwargs)
        kwargs = {
            'zone': z3, wdays[now.weekday()]: True, 'mode': 'H',
            'start_time': (now - datetime.timedelta(minutes=2)).time(),
            'end_time': (now + datetime.timedelta(minutes=2)).time(),
        }
        slot_z3 = Slot.objects.create(**kwargs)
        derog_z3 = Derogation.objects.create(
            start_dt = timezone.now() - datetime.timedelta(minutes=2),
            end_dt = timezone.now() + datetime.timedelta(minutes=2),
            mode = 'A'
        )
        derog_z3.zones = [z3]
        self.assertEqual(Zone.objects.get_modes(), {'1':'C','2':'E','3':'A'})

class SlotModelTest(TestCase):

    def test_string_representation(self):
        zone = Zone(num=1)
        slot = Slot(
            zone=zone, mon=True, wed=True, fri=True, sun=True,
            start_time = datetime.time(4, 2), end_time = datetime.time(15, 54),
            mode = 'E'
        )
        self.assertEqual(str(slot), "Z1 04:02:00-15:54:00 [L*M*V*D] Eco")

    def test_is_active_queryset_method(self):
        zone = Zone(num=1)
        wdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        now = timezone.localtime(timezone.now())
        if now.time().hour < 1:
            raise Exception("This test cannot be run between 00:00 and 01:00")
        kwargs = {
            'zone': zone, wdays[now.weekday()]: True, 'mode': 'E',
            'start_time': (now - datetime.timedelta(hours=1)).time(),
            'end_time': (now - datetime.timedelta(minutes=2)).time()
        }
        past_slot = Slot.objects.create(**kwargs)
        kwargs = {
            'zone': zone, wdays[now.weekday()]: True, 'mode': 'E',
            'start_time': now.time(),
            'end_time': (now + datetime.timedelta(minutes=2)).time()
        }
        active_slot = Slot.objects.create(**kwargs)
        kwargs = {
            'zone': zone, wdays[now.weekday()]: True, 'mode': 'E',
            'start_time': (now + datetime.timedelta(minutes=2)).time(),
            'end_time': (now - datetime.timedelta(hours=1)).time()
        }
        future_slot = Slot.objects.create(**kwargs)
        kwargs = {
            'zone': zone, wdays[(now.weekday() - 1) % 7]: True, 'mode': 'E',
            'start_time': (now - datetime.timedelta(hours=1)).time(),
            'end_time': (now - datetime.timedelta(minutes=2)).time()
        }
        yesterday_slot = Slot.objects.create(**kwargs)
        kwargs = {
            'zone': zone, wdays[(now.weekday() + 1) % 7]: True, 'mode': 'E',
            'start_time': (now - datetime.timedelta(hours=1)).time(),
            'end_time': (now - datetime.timedelta(minutes=2)).time()
        }
        tomorrow_slot = Slot.objects.create(**kwargs)
        queryset = Slot.objects.is_active()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0], active_slot)

class DerogationModelTest(TestCase):

    def create_entries_for_active_tests(self):
        self.past_derog = Derogation.objects.create(
            start_dt = timezone.now() - datetime.timedelta(days=1),
            end_dt = timezone.now() - datetime.timedelta(minutes=2),
            mode = 'E'
        )
        self.active_derog = Derogation.objects.create(
            start_dt = timezone.now(),
            end_dt = timezone.now() + datetime.timedelta(minutes=2),
            mode = 'E'
        )
        self.future_derog = Derogation.objects.create(
            start_dt = timezone.now() + datetime.timedelta(minutes=2),
            end_dt = timezone.now() + datetime.timedelta(days=1),
            mode = 'E'
        )

    def test_string_representation(self):
        zone2 = Zone.objects.create(num=2)
        zone3 = Zone.objects.create(num=3)
        tz = timezone.get_default_timezone()
        start = timezone.make_aware(
            datetime.datetime(2015, 2, 25, 17, 24), tz
        )
        end = timezone.make_aware(
            datetime.datetime(2015, 3, 18, 18, 12), tz
        )
        derog = Derogation.objects.create(start_dt=start, end_dt=end, mode='H')
        derog.zones = [zone2, zone3]
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
