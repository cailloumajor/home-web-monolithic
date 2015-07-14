# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heating', '0004_auto_20150611_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='derogation',
            name='active',
        ),
    ]
