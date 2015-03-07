# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heating', '0005_remove_derogation_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='derogation',
            name='end_dt',
            field=models.DateTimeField(verbose_name="fin d'effet"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='derogation',
            name='start_dt',
            field=models.DateTimeField(verbose_name="prise d'effet"),
            preserve_default=True,
        ),
    ]
