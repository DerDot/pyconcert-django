# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('pyconcert', '0003_auto_20150511_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='favoritedby',
            field=models.ManyToManyField(related_name='favorit_artists', to=settings.AUTH_USER_MODEL)
        ),
    ]
