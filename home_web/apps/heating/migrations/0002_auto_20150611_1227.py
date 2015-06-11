# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heating', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slot',
            name='end_time',
            field=models.TimeField(verbose_name='heure de fin'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='slot',
            name='fri',
            field=models.BooleanField(default=False, verbose_name='vendredi'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='slot',
            name='mode',
            field=models.CharField(default=None, verbose_name='mode de fonctionnement', choices=[('E', 'Eco'), ('H', 'Hors gel'), ('A', 'Arrêt')], max_length=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='slot',
            name='mon',
            field=models.BooleanField(default=False, verbose_name='lundi'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='slot',
            name='sat',
            field=models.BooleanField(default=False, verbose_name='samedi'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='slot',
            name='start_time',
            field=models.TimeField(verbose_name='heure de début'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='slot',
            name='sun',
            field=models.BooleanField(default=False, verbose_name='dimanche'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='slot',
            name='thu',
            field=models.BooleanField(default=False, verbose_name='jeudi'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='slot',
            name='tue',
            field=models.BooleanField(default=False, verbose_name='mardi'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='slot',
            name='wed',
            field=models.BooleanField(default=False, verbose_name='mercredi'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='zone',
            name='desc',
            field=models.CharField(blank=True, verbose_name='description', max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='zone',
            name='num',
            field=models.PositiveSmallIntegerField(serialize=False, choices=[(1, 1), (2, 2), (3, 3), (4, 4)], verbose_name='numéro de zone', primary_key=True),
            preserve_default=True,
        ),
    ]
