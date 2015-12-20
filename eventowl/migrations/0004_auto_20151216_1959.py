# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventowl', '0003_visitorlocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitorlocation',
            name='city',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='visitorlocation',
            name='country',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
