# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heating', '0002_auto_20150611_1227'),
    ]

    operations = [
        migrations.CreateModel(
            name='Derogation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('mode', models.CharField(default=None, verbose_name='mode de fonctionnement', max_length=1, choices=[('E', 'Eco'), ('H', 'Hors gel'), ('A', 'Arrêt')])),
                ('creation_dt', models.DateTimeField(verbose_name='date/heure de création', auto_now_add=True)),
                ('start_dt', models.DateTimeField(verbose_name="date/heure de prise d'effet")),
                ('end_dt', models.DateTimeField(verbose_name="date/heure de fin d'effet")),
                ('active', models.BooleanField(default=False, editable=False)),
                ('zones', models.ManyToManyField(to='heating.Zone')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
