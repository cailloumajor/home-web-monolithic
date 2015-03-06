#-*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

class DerogationQuerySet(models.QuerySet):
    def is_active(self):
        now = timezone.now()
        return self.filter(start_dt__lte=now, end_dt__gte=now)
