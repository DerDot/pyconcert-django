from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return unicode(self.name)
    
class Event(models.Model):
    venue = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    ticket_url = models.URLField()
    artists = models.ManyToManyField(Artist)
    
    def __unicode__(self):
        artists = [unicode(artist) for artist in self.artists.all()]
        name = u"{} at {} on {}".format(u", ".join(artists),
                                      unicode(self.venue),
                                      unicode(self.date.strftime("%Y-%m-%d")))
        return name