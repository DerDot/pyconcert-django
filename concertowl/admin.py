from django.contrib import admin
from concertowl.models import Artist, Event, RecommendedArtist, Preview, Record

admin.site.register(Artist)
admin.site.register(Event)
admin.site.register(RecommendedArtist)
admin.site.register(Preview)
admin.site.register(Record)