# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookowl', '0010_auto_20151207_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preview',
            name='image',
            field=models.URLField(unique=True),
        ),
    ]
