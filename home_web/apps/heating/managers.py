#-*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

class ZoneManager(models.Manager):
    DEFAULT_MODE = 'C'

    def _get_zone_mode(self, zone):
        """"
        Return current active mode for zone passed in argument,
        taking eventual derogation in account.
        """
        try:
            return zone.derogation_set.is_active().get().mode
        except ObjectDoesNotExist:
            pass
        try:
            return zone.slot_set.is_active().get().mode
        except ObjectDoesNotExist:
            pass
        return self.DEFAULT_MODE

    def get_modes(self):
        return {
            str(z.num):self._get_zone_mode(z) for z in self.all()
        }

class SlotQuerySet(models.QuerySet):
    def is_active(self):
        now = timezone.localtime(timezone.now())
        time = now.time()
        wday = [
            'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
        ][now.weekday()]
        return self.filter(**{wday:True}).filter(
            start_time__lte = time, end_time__gte = time
        )

class DerogationQuerySet(models.QuerySet):
    def is_active(self):
        now = timezone.now()
        return self.filter(start_dt__lte=now, end_dt__gte=now)

    def is_outdated(self):
        return self.filter(end_dt__lt=timezone.now())
