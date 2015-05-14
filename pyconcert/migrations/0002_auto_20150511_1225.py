# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings



class Migration(migrations.Migration):

    dependencies = [
        ('pyconcert', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommendedartist',
            name='score',
            field=models.FloatField(null=True),
        ),
        migrations.CreateModel(
            name='RecommendedArtist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.FloatField()),
                ('artist', models.ForeignKey(to='pyconcert.Artist')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
