# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concertowl', '0009_auto_20151209_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preview',
            name='image',
            field=models.URLField(unique=True),
        ),
    ]
