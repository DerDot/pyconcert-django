# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyconcert', '0003_artist_recommendedtos'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='genre',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
