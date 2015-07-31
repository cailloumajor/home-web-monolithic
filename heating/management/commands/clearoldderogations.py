# -*- coding: utf-8 -*-

import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...models import Derogation


class Command(BaseCommand):

    help = "Removes derogations with end older than given days."
    missing_args_message = "You must provide a number of days."

    def add_arguments(self, parser):
        parser.add_argument('days', type=int)

    def handle(self, **options):
        days_old = options['days']
        deadline = timezone.now() - datetime.timedelta(days=days_old)
        qs = Derogation.objects.filter(end_dt__lte=deadline)
        count = qs.count()
        qs.delete()

        self.stdout.write("{} derogation(s) removed.".format(count))
