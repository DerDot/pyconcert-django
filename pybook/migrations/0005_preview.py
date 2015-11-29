# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybook', '0004_remove_author_binding'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('originator', models.CharField(max_length=200)),
                ('image', models.URLField()),
                ('description', models.TextField()),
                ('link', models.URLField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
