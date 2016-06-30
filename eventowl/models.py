import uuid

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    city = models.CharField(max_length=200)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.user.username


class Preview(models.Model):
    image = models.URLField(max_length=200, unique=True)
    description = models.TextField()
    link = models.URLField(max_length=200)
    alttext = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = 'updated_at'

    def __str__(self):
        return self.description


class VisitorLocation(models.Model):
    country = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)

    def __str__(self):
        return '{} - {}'.format(self.city, self.country)
