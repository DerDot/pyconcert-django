# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concertowl', '0002_auto_20150511_1225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommendedartist',
            name='artist',
            field=models.ForeignKey(
                related_name='recommendation', to='concertowl.Artist', on_delete=models.CASCADE),
        ),
    ]
