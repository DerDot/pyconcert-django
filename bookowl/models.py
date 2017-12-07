from django.db import models
from django.contrib.auth.models import User
from eventowl import models as base_models


class Author(models.Model):
    name = models.CharField(max_length=200)
    subscribers = models.ManyToManyField(User, related_name='authors')
    recommendedtos = models.ManyToManyField(User, through='RecommendedAuthor')
    favoritedby = models.ManyToManyField(User, related_name='favorit_authors')

    def __str__(self):
        return self.name


class RecommendedAuthor(models.Model):
    artist = models.ForeignKey(Author, related_name="recommendation", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(null=True)


class Book(models.Model):
    title = models.CharField(max_length=300)
    isbn = models.CharField(max_length=20, null=True)
    date = models.DateField()
    buy_url = models.URLField(max_length=300)
    authors = models.ManyToManyField(Author, related_name='books')

    def __str__(self):
        author_names = [author.name.title() for author in
                        self.authors.all()]
        name = "{} by {} released on {}".format(self.title,
                                                 ", ".join(author_names),
                                                 str(self.date.strftime("%Y-%m-%d")))
        return name


class Preview(base_models.Preview):
    pass