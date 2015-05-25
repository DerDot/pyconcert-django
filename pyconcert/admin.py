from django.contrib import admin
from pyconcert.models import Artist, Event, RecommendedArtist

admin.site.register(Artist)
admin.site.register(Event)
admin.site.register(RecommendedArtist)