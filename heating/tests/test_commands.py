# -*- coding: utf-8 -*-

import datetime
import logging
from os import devnull

from django.test import TestCase, override_settings
from django.utils import timezone
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils.six import StringIO

from django_dynamic_fixture import G, F

from ..models import Slot, Derogation, PilotwireLog
from ..pilotwire.test import TestServer
from ..log import PilotwireHandler


PILOTWIRE_TEST_SERVER_PORT = 8888


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


@override_settings(PILOTWIRE_CONTROLER={
    'address': 'localhost',
    'port': PILOTWIRE_TEST_SERVER_PORT,
})
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

    def test_order_with_no_zone(self):
        out = StringIO()
        expected_out = "{'1': 'C', '2': 'C', '3': 'C', '4': 'C'}"
        with TestServer(PILOTWIRE_TEST_SERVER_PORT):
            call_command(self.cmd, stdout=out)
        self.assertIn(expected_out, out.getvalue())

    def test_order_with_four_zones(self):
        out = StringIO()
        expected_out = "{'1': 'E', '2': 'H', '3': 'A', '4': 'E'}"
        now = timezone.now()
        local_now = timezone.localtime(now)
        time_start =  (local_now - datetime.timedelta(minutes=2)).time()
        time_end = (local_now + datetime.timedelta(minutes=2)).time()
        today = [
            'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
        ][local_now.weekday()]
        dt_start = now -datetime.timedelta(minutes=2)
        dt_end = now + datetime.timedelta(minutes=2)
        for i in range(1, 4):
            kwargs = {
                'zone': F(num=i),
                'mode': ('E', 'H', 'A')[i-1],
                'start_time': time_start,
                'end_time': time_end,
                today: True,
            }
            G(Slot, **kwargs)
        G(Derogation, zones=[F(num=4)], mode='E',
          start_dt=dt_start, end_dt=dt_end)
        with TestServer(PILOTWIRE_TEST_SERVER_PORT):
            call_command(self.cmd, stdout=out)
        self.assertIn(expected_out, out.getvalue())


@override_settings(PILOTWIRE_CONTROLER={
    'address': 'localhost',
    'port': PILOTWIRE_TEST_SERVER_PORT,
})
class SetPilotwireLoggingTest(TestCase):

    cmd = 'setpilotwire'

    @classmethod
    def setUpClass(cls):
        super(SetPilotwireLoggingTest, cls).setUpClass()
        cls.out = open(devnull, 'w')
        logger = logging.getLogger('setpilotwire')
        logger.setLevel(logging.INFO)
        handler = PilotwireHandler(logLength=10)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    @classmethod
    def tearDownClass(cls):
        cls.out.close()
        super(SetPilotwireLoggingTest, cls).tearDownClass()

    def test_success_logging(self):
        with TestServer(PILOTWIRE_TEST_SERVER_PORT):
            call_command(self.cmd, stdout=self.out)
        self.assertEqual(PilotwireLog.objects.count(), 1)
        log_entry = PilotwireLog.objects.all()[0]
        self.assertEqual(log_entry.level, 'INFO')
        self.assertIn("Modes set on pilotwire controler", log_entry.message)

    def test_error_logging(self):
        try:
            call_command(self.cmd, stdout=self.out)
        except CommandError:
            pass
        self.assertEqual(PilotwireLog.objects.count(), 1)
        log_entry = PilotwireLog.objects.all()[0]
        self.assertEqual(log_entry.level, 'ERROR')
        self.assertIn("ConnectionRefusedError: [Errno 111] Connection refused",
                      log_entry.message)

    def test_log_max_length(self):
        for i in range(10):
            G(PilotwireLog)
        self.assertEqual(PilotwireLog.objects.count(), 10)
        try:
            call_command(self.cmd, stdout=self.out)
        except CommandError:
            pass
        self.assertEqual(PilotwireLog.objects.count(), 10)
        self.assertEqual(PilotwireLog.objects.all()[0].level, 'ERROR')

    def test_command_fired_by_derogation_signals(self):
        now = timezone.now()
        G(Derogation, mode='E',
          start_dt=now-datetime.timedelta(minutes=2),
          end_dt=now+datetime.timedelta(minutes=2))
        self.assertEqual(PilotwireLog.objects.count(), 2)
        self.assertIn(
            "Active derogation created, going to set pilotwire modes",
            PilotwireLog.objects.all()[1].message
        )
        Derogation.objects.last().delete()
        self.assertEqual(PilotwireLog.objects.count(), 4)
        self.assertIn(
            "Active derogation removed, going to set pilotwire modes",
            PilotwireLog.objects.all()[1].message
        )
