# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookowl', '0006_preview_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='preview',
            name='name',
            field=models.CharField(default='otter', max_length=200),
            preserve_default=False,
        ),
    ]
