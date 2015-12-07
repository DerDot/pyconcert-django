# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookowl', '0002_auto_20150601_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='buy_url',
            field=models.URLField(max_length=300),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=300),
        ),
    ]
