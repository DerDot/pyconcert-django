# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concertowl', '0008_auto_20151207_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='preview',
            name='city',
            field=models.CharField(default='berlin', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='preview',
            name='country',
            field=models.CharField(default='germany', max_length=200),
            preserve_default=False,
        ),
    ]
