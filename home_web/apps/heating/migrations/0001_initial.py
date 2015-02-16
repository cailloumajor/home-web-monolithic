# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mon', models.BooleanField(default=False, verbose_name=b'lundi')),
                ('tue', models.BooleanField(default=False, verbose_name=b'mardi')),
                ('wed', models.BooleanField(default=False, verbose_name=b'mercredi')),
                ('thu', models.BooleanField(default=False, verbose_name=b'jeudi')),
                ('fri', models.BooleanField(default=False, verbose_name=b'vendredi')),
                ('sat', models.BooleanField(default=False, verbose_name=b'samedi')),
                ('sun', models.BooleanField(default=False, verbose_name=b'dimanche')),
                ('start_time', models.TimeField(verbose_name=b'heure de d\xc3\xa9but')),
                ('end_time', models.TimeField(verbose_name=b'heure de fin')),
                ('mode', models.CharField(default=None, max_length=1, verbose_name=b'mode de fonctionnement', choices=[(b'E', b'Eco'), (b'H', b'Hors gel'), (b'A', b'Arr\xc3\xaat')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('num', models.PositiveSmallIntegerField(serialize=False, verbose_name=b'num\xc3\xa9ro de zone', primary_key=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4)])),
                ('desc', models.CharField(max_length=50, verbose_name=b'description', blank=True)),
            ],
            options={
                'ordering': ['num'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='slot',
            name='zone',
            field=models.ForeignKey(to='heating.Zone'),
            preserve_default=True,
        ),
    ]
