from pyconcert.models import Artist, Event
from pyconcert.api_calls import events_for_artists_bandsintown
from django.core.management.base import BaseCommand

def _db_artists(api_event):
    artists = []
    for event_artist in api_event.artists:
        artist, created = Artist.objects.get_or_create(name=event_artist)
        if created:
            artist.save()
        artists.append(artist)
    return artists

def update_events(artists):
    api_events = events_for_artists_bandsintown(artists, "Berlin")
    for api_event in api_events:
        event, created = Event.objects.get_or_create(venue=api_event.venue,
                                             city=api_event.city,
                                             country=api_event.country,
                                             date=api_event.date,
                                             time=api_event.time,
                                             ticket_url=api_event.ticket_url)
        if created:
            event.save()
        for db_artist in _db_artists(api_event):
            event.artists.add(db_artist)

class Command(BaseCommand):
    help = 'Update events for all artists. Used by cron.'

    def handle(self, *args, **options):
        artists = [artist.name for artist in
                   Artist.objects.all()]
        update_events(artists)

