from pyconcert.models import Artist, Event
from pyconcert.api_calls import events_for_artists_bandsintown
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Update events for all artists. Used by cron.'
    
    def handle(self, *args, **options):
        artists = [artist.name for artist in
                   Artist.objects.all()]
        api_events = events_for_artists_bandsintown(artists, "Berlin")
        for api_event in api_events:
            event, created = Event.objects.get_or_create(venue=api_event.venue,
                                                         city=api_event.city,
                                                         country=api_event.country,
                                                         artists=", ".join(api_event.artists),
                                                         date=api_event.date,
                                                         time=api_event.time,
                                                         ticket_url=api_event.ticket_url)
            if created:
                event.save()