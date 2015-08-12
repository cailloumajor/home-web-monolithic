# -*- coding: utf-8 -*-

import logging
from os import devnull

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.management import call_command, CommandError

from .models import Derogation


@receiver(
    [post_save, post_delete],
    sender=Derogation,
    dispatch_uid='derog_pilotwire'
)
def derogation_active_receiver(sender, **kwargs):
    if not kwargs['instance'].active():
        return
    logger = logging.getLogger('setpilotwire')
    action = 'created' if 'created' in kwargs else 'removed'
    logger.info(
        "Active derogation {}, going to set pilotwire modes".format(action))
    with open(devnull, 'w') as null:
        try:
            call_command('setpilotwire', stdout=null)
        except CommandError:
            pass
