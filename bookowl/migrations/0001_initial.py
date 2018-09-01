# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('binding', models.CharField(max_length=200)),
                ('favoritedby', models.ManyToManyField(
                    related_name='favorit_authors', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('isbn', models.CharField(max_length=20)),
                ('date', models.DateField()),
                ('buy_url', models.URLField()),
                ('authors', models.ManyToManyField(
                    related_name='books', to='bookowl.Author')),
            ],
        ),
        migrations.CreateModel(
            name='RecommendedAuthor',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('score', models.FloatField(null=True)),
                ('artist', models.ForeignKey(related_name='recommendation',
                                             to='bookowl.Author', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(
                    to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='recommendedtos',
            field=models.ManyToManyField(
                to=settings.AUTH_USER_MODEL, through='bookowl.RecommendedAuthor'),
        ),
        migrations.AddField(
            model_name='author',
            name='subscribers',
            field=models.ManyToManyField(
                related_name='authors', to=settings.AUTH_USER_MODEL),
        ),
    ]
