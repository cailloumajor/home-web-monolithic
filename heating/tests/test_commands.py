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
        derogs = []
        for d in range(1, 4):
            end = timezone.now() - datetime.timedelta(days=d, minutes=5)
            derogs.append(G(Derogation, mode='E', end_dt=end))
        out = StringIO()
        call_command(self.cmd, '2', stdout=out)
        cmd_out = out.getvalue()
        self.assertIn("2 derogation(s) removed", cmd_out)
        self.assertNotIn(str(derogs[0]), cmd_out)
        self.assertIn(str(derogs[1]), cmd_out)
        self.assertIn(str(derogs[2]), cmd_out)
        self.assertEqual(Derogation.objects.count(), 1)

    def test_clear_3_days_old(self):
        derogs = []
        for d in range(1, 4):
            end = timezone.now() - datetime.timedelta(days=d, minutes=5)
            derogs.append(G(Derogation, mode='H', end_dt=end))
        out = StringIO()
        call_command(self.cmd, '3', stdout=out)
        cmd_out = out.getvalue()
        self.assertIn("1 derogation(s) removed", cmd_out)
        self.assertNotIn(str(derogs[0]), cmd_out)
        self.assertNotIn(str(derogs[1]), cmd_out)
        self.assertIn(str(derogs[2]), cmd_out)
        self.assertEqual(Derogation.objects.count(), 2)


class SetPilotwireTest(TestCase):

    cmd = 'setpilotwire'

    def test_argument_passing(self):
        self.assertRaisesRegex(
            CommandError, "Error: unrecognized arguments: test",
            call_command, self.cmd, 'test')

    def test_no_xmlrpc_server(self):
        self.assertRaisesRegex(
            CommandError,
            "ConnectionRefusedError: \[Errno 111\] Connection refused",
            call_command, self.cmd)
