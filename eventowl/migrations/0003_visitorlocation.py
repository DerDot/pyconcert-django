# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventowl', '0002_remove_userprofile_api_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitorLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
            ],
        ),
    ]
