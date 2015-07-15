# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils.six import StringIO

from django_dynamic_fixture import G

from ..models import Derogation


class ClearOldDerogationsTests(TestCase):

    cmd = 'clearoldderogations'

    def test_no_argument(self):
        self.assertRaisesRegex(
            CommandError, "You must provide a number of days.",
            call_command, self.cmd)

    def test_too_much_arguments(self):
        self.assertRaisesRegex(
            CommandError, "Error: unrecognized arguments: 2",
            call_command, self.cmd, '1', '2')

    def test_bad_argument_type(self):
        self.assertRaisesRegex(
            CommandError, "Error: argument days: invalid int value: 'a'",
            call_command, self.cmd, 'a')

    def test_clear_2_days_old(self):
        for d in range(1, 4):
            end = timezone.now() - datetime.timedelta(days=d, minutes=5)
            G(Derogation, mode='E', end_dt=end)
        out = StringIO()
        call_command(self.cmd, '2', stdout=out)
        self.assertIn('2', out.getvalue())
        self.assertEqual(Derogation.objects.count(), 1)

    def test_clear_3_days_old(self):
        for d in range(1, 4):
            end = timezone.now() - datetime.timedelta(days=d, minutes=5)
            G(Derogation, mode='H', end_dt=end)
        out = StringIO()
        call_command(self.cmd, '3', stdout=out)
        self.assertIn('1', out.getvalue())
        self.assertEqual(Derogation.objects.count(), 2)
