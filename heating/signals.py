# -*- coding: utf-8 -*-

import logging
from os import devnull

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.management import call_command
from django.conf import settings
import django_rq

from .models import Derogation


@receiver(
    [post_save, post_delete],
    sender=Derogation,
    dispatch_uid='derog_pilotwire'
)
def derogation_active_receiver(sender, **kwargs):
    if not settings.RQ_ACTIVE or not kwargs['instance'].active():
        return
    logger = logging.getLogger('setpilotwire')
    action = 'created' if 'created' in kwargs else 'removed'
    logger.info(
        "Active derogation {}, going to set pilotwire modes".format(action))
    django_rq.enqueue(call_command, 'setpilotwire', async=True, result_ttl=0)
