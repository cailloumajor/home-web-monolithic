#-*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

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
