# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pybook', '0005_preview'),
    ]

    operations = [
        migrations.AddField(
            model_name='preview',
            name='date',
            field=models.DateField(default=datetime.datetime(2016, 1, 1, 0, 0)),
            preserve_default=False,
        ),
    ]
