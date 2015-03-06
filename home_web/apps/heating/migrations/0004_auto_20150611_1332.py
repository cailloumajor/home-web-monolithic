# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heating', '0003_derogation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='derogation',
            options={'ordering': ['creation_dt']},
        ),
    ]
