# -*- coding: utf-8 -*-

import logging
from xmlrpc.client import ServerProxy
from pprint import pformat

from django.core.management import BaseCommand, CommandError
from django.conf import settings

from ...models import Zone


logger = logging.getLogger('setpilotwire')


class Command(BaseCommand):

    help = "Set modes outputs on pilotwire controler"

    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            dest='async',
            default=False,
            help="Command ran asynchronously"
        )

    def handle(self, **options):
        try:
            xmlrpc_url = 'http://{host}:{port}/'.format(
                host = settings.PILOTWIRE_CONTROLER['address'],
                port = settings.PILOTWIRE_CONTROLER['port'],
            )
        except AttributeError:
            return

        # Get current modes dict for all existing zones
        modes = Zone.objects.get_modes()

        try:
            # Pass modes to pilotwire controler by XML-RPC
            try:
                xrserv = ServerProxy(xmlrpc_url)
                xrresp = xrserv.setModes(modes)
            except Exception as err:
                raise CommandError("{}: {}".format(err.__class__.__name__, err))
                if not all(item in xrresp.items() for item in modes.items()):
                    raise CommandError(
                        "Pilotwire controler did not respond same modes as sent"
                    )
        except CommandError as cmderr:
            logger.error(cmderr)
            if options['async']:
                return
            else:
                raise cmderr

        success_msg = "Modes set on pilotwire controler : {}".format(
            pformat(xrresp))
        if not options['async']:
            self.stdout.write(success_msg)
        logger.info(success_msg)
