from django.contrib import admin
from concertowl.models import Artist, Event, RecommendedArtist, Preview, Record
from eventowl.admin import MoreItemsAdmin


@admin.register(Event)
class RecordAdmin(MoreItemsAdmin):
    list_display = ('venue', 'city', 'date')


@admin.register(Record)
class RecordAdmin(MoreItemsAdmin):
    list_display = ('title', 'date')


admin.site.register(Artist, MoreItemsAdmin)
admin.site.register(RecommendedArtist, MoreItemsAdmin)
admin.site.register(Preview, MoreItemsAdmin)