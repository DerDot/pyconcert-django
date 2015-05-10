from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    name = models.CharField(max_length=200)
    genre = models.CharField(max_length=200, null=True)
    subscribers = models.ManyToManyField(User, related_name='artists')
    recommendedtos = models.ManyToManyField(User, related_name='recommended_artists')

    def __unicode__(self):
        return unicode(self.name)

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

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    city = models.CharField(max_length=200)

    def __unicode__(self):
        return self.user.username
