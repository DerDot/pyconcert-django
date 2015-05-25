from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    city = models.CharField(max_length=200)
    USA = 'US'
    FRANCE = 'FR'
    CHINA = 'CN'
    ENGLAND = 'UK'
    CANADA = 'CA'
    GERMANY = 'DE'
    JAPAN = 'JP'
    ITALY = 'IT'
    SPAIN = 'ES'
    API_REGIONS = ((USA, 'USA'),
                   (FRANCE, 'France'),
                   (CHINA, 'China'),
                   (ENGLAND, 'England'),
                   (CANADA, 'Canada'),
                   (GERMANY, 'Germany'),
                   (JAPAN, 'Japan'),
                   (ITALY, 'Italy'),
                   (SPAIN, 'Spain'))
    api_region = models.CharField(max_length=2,
                                  choices=API_REGIONS,
                                  default=USA)

    def __unicode__(self):
        return self.user.username