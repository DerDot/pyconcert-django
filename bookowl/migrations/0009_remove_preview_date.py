# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookowl', '0008_auto_20151129_1455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preview',
            name='date',
        ),
    ]
