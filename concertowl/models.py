from django.db import models
from django.contrib.auth.models import User
from eventowl import models as base_models

class Artist(models.Model):
    name = models.CharField(max_length=200)
    genre = models.CharField(max_length=200, null=True)
    subscribers = models.ManyToManyField(User, related_name='artists')
    recommendedtos = models.ManyToManyField(User, through='RecommendedArtist')
    favoritedby = models.ManyToManyField(User, related_name='favorit_artists')

    def __str__(self):
        return self.name


class RecommendedArtist(models.Model):
    artist = models.ForeignKey(Artist, related_name="recommendation", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(null=True)


class Event(models.Model):
    venue = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    ticket_url = models.URLField()
    artists = models.ManyToManyField(Artist, related_name='events')

    def __str__(self):
        artist_names = [artist.name.title() for artist in
                        self.artists.all()]
        name = "{} at {} on {}".format(", ".join(artist_names),
                                        str(self.venue),
                                        str(self.date.strftime("%Y-%m-%d")))
        return name


class Preview(base_models.Preview):
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)


class Record(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    details_url = models.URLField()
    artists = models.ManyToManyField(Artist, related_name='releases')

    def __str__(self):
        artist_names = [artist.name.title() for artist in
                        self.artists.all()]
        name = "{} by {} on {}".format(self.title,
                                        ", ".join(artist_names),
                                        str(self.date.strftime("%Y-%m-%d")))
        return name
