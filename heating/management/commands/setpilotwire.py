# -*- coding: utf-8 -*-

from xmlrpc.client import ServerProxy
from pprint import pformat

from django.core.management import BaseCommand, CommandError
from django.conf import settings

from ...models import Zone


class Command(BaseCommand):

    help = "Set modes outputs on pilotwire controler"

    def handle(self, **options):
        # Get current modes dict for all existing zones
        modes = Zone.objects.get_modes()

        xmlrpc_url = 'http://{host}:{port}/'.format(
            host = settings.PILOTWIRE_CONTROLER['address'],
            port = settings.PILOTWIRE_CONTROLER['port'],
        )

        # Pass modes to pilotwire controler by XML-RPC
        xrserv = ServerProxy(xmlrpc_url)
        try:
            xrresp = xrserv.setModes(modes)
        except Exception as err:
            raise CommandError("{}: {}".format(err.__class__.__name__, err))
        if not all(item in xrresp.items() for item in modes.items()):
            raise CommandError(
                "Pilotwire controler did not respond same modes as sent"
            )

        self.stdout.write(
            "Modes set on pilotwire controler : {}".format(pformat(xrresp))
        )
