# -*- coding: utf-8 -*-


from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('bookowl', '0009_remove_preview_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='preview',
            options={'get_latest_by': 'updated_at'},
        ),
        migrations.AddField(
            model_name='preview',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 7, 15, 56, 37, 196905), auto_now=True),
            preserve_default=False,
        ),
    ]
