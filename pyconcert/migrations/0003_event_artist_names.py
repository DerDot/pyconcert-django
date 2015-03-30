# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyconcert', '0002_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='artist_names',
            field=models.CharField(default=b'', max_length=200, editable=False),
            preserve_default=True,
        ),
    ]
