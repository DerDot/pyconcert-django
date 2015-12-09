from django.db import models
from django.contrib.auth.models import User
from eventowl import models as base_models

class Artist(models.Model):
    name = models.CharField(max_length=200)
    genre = models.CharField(max_length=200, null=True)
    subscribers = models.ManyToManyField(User, related_name='artists')
    recommendedtos = models.ManyToManyField(User, through='RecommendedArtist')
    favoritedby = models.ManyToManyField(User, related_name='favorit_artists')

    def __unicode__(self):
        return unicode(self.name)


class RecommendedArtist(models.Model):
    artist = models.ForeignKey(Artist, related_name="recommendation")
    user = models.ForeignKey(User)
    score = models.FloatField(null=True)


class Event(models.Model):
    venue = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    ticket_url = models.URLField()
    artists = models.ManyToManyField(Artist, related_name='events')

    def __unicode__(self):
        artist_names = [artist.name.title() for artist in
                        self.artists.all()]
        name = u"{} at {} on {}".format(u", ".join(artist_names),
                                        unicode(self.venue),
                                        unicode(self.date.strftime("%Y-%m-%d")))
        return name

class Preview(base_models.Preview):
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
