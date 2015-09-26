# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pybook', '0003_auto_20150810_1710'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='binding',
        ),
    ]
