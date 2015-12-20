from django.core.management.base import BaseCommand

from eventowl.utils.common_functions import EventConnector
from eventowl.models import UserProfile

from concertowl.models import Artist, Event
from concertowl.api_calls import events_for_artists_bandsintown
from eventowl.utils.django_helpers import set_if_different


def _all_cities():
    cities = set()
    for user_profile in UserProfile.objects.all():
        cities.add(user_profile.city.lower())
    return cities


class ConcertConnector(EventConnector):
    originator_name = 'artists'
    originator_model = Artist

    def _get_events(self, artists, cities=None):
        if cities is None:
            cities = _all_cities()

        all_api_events = []
        for city in cities:
            print(("Updating events for", city))
            api_events = events_for_artists_bandsintown(artists, city)
            all_api_events.extend(api_events)

        return all_api_events

    def _get_or_create_object(self, api_event):
        exists = Event.objects.filter(city=api_event.city,
                                      country=api_event.country,
                                      date=api_event.date,
                                      ticket_url=api_event.ticket_url)

        if exists:
            event = Event.objects.get(city=api_event.city,
                                      country=api_event.country,
                                      date=api_event.date,
                                      ticket_url=api_event.ticket_url)
            should_save = set_if_different(event, 'venue', api_event.venue)
            should_save |= set_if_different(event, 'time', api_event.time)
        else:
            event = Event.objects.create(city=api_event.city,
                                         country=api_event.country,
                                         date=api_event.date,
                                         ticket_url=api_event.ticket_url,
                                         venue=api_event.venue,
                                         time=api_event.time)
            should_save = True
        
        return event, should_save
    
    def _message_for_originator(self, artist):
        return "New concert by {}".format(artist.name.title()) 


class Command(BaseCommand):
    help = 'Update events for all artists. Used by cron.'

    def handle(self, *args, **options):
        artists = [artist.name for artist in
                   Artist.objects.all()]
        con = ConcertConnector()
        con.update_events(artists)