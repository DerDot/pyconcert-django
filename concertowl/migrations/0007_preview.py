# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concertowl', '0006_auto_20150523_1829'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.URLField()),
                ('description', models.TextField()),
                ('link', models.URLField()),
                ('alttext', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
