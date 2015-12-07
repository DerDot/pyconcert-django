# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookowl', '0007_preview_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='preview',
            old_name='name',
            new_name='alttext',
        ),
        migrations.RemoveField(
            model_name='preview',
            name='originator',
        ),
    ]
