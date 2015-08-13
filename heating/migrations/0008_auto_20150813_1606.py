# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heating', '0007_pilotwirelog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pilotwirelog',
            name='timestamp',
            field=models.DateTimeField(verbose_name='date/heure', db_index=True, auto_now_add=True),
        ),
    ]
