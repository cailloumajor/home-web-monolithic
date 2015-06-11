# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase

from ..models import Zone, Slot

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

