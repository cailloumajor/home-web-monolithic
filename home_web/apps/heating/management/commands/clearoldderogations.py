# -*- coding: utf-8 -*-

import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ...models import Derogation


class Command(BaseCommand):

    args = 'days'
    help = "Removes derogations with end older than given days."

    def handle(self, *days, **options):
        if not len(days) == 1:
            raise CommandError("Bad number of arguments, one required.")
        try:
            days = int(days[0])
        except ValueError:
            raise CommandError(
                "Numeric argument required, '{}' given.".format(days[0]))
        deadline = timezone.now() - datetime.timedelta(days=days)
        qs = Derogation.objects.filter(end_dt__lte=deadline)
        count = qs.count()
        qs.delete()

        self.stdout.write("{} derogation(s) removed.".format(count))
