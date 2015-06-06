# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.utils import timezone

from ..models import Zone, Slot, Derogation

class ZoneModelTest(TestCase):

    def test_string_representation(self):
        zone = Zone(num=1)
        self.assertEqual(str(zone), 'Z{}'.format(zone.num))

class SlotModelTest(TestCase):

    def test_string_representation(self):
        zone = Zone(num=1)
        slot = Slot(
            zone=zone, mon=True, wed=True, fri=True, sun=True,
            start_time = datetime.time(4, 2), end_time = datetime.time(15, 54),
            mode = 'E'
        )
        self.assertEqual(str(slot), "Z1 04:02:00-15:54:00 [L*M*V*D] Eco")

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
