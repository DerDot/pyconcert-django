from django.contrib import admin
from pyconcert.models import Artist, Event, UserProfile

admin.site.register(Artist)
admin.site.register(Event)
admin.site.register(UserProfile)