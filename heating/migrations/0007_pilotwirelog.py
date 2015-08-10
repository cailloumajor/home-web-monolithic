# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heating', '0006_auto_20150611_1337'),
    ]

    operations = [
        migrations.CreateModel(
            name='PilotwireLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('timestamp', models.DateTimeField(verbose_name='date/heure', auto_now_add=True)),
                ('level', models.CharField(verbose_name='niveau', max_length=10)),
                ('message', models.TextField()),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
