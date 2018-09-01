# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('concertowl', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecommendedArtist',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('score', models.FloatField()),
                ('artist', models.ForeignKey(
                    to='concertowl.Artist', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(
                    to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterField(
            model_name='recommendedartist',
            name='score',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='recommendedtos',
            field=models.ManyToManyField(
                to=settings.AUTH_USER_MODEL, through='concertowl.RecommendedArtist'),
        ),
    ]
