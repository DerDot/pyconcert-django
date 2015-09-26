from django.core.management.base import BaseCommand

from eventowl.common_utils import EventConnector
from eventowl.models import UserProfile

from pyconcert.models import Artist, Event
from pyconcert.api_calls import events_for_artists_bandsintown


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
            print "Updating events for", city
            api_events = events_for_artists_bandsintown(artists, city)
            all_api_events.extend(api_events)

        return all_api_events

    def _get_or_create_object(self, api_event):
        release, created = Event.objects.get_or_create(venue=api_event.venue,
                                                       city=api_event.city,
                                                       country=api_event.country,
                                                       date=api_event.date,
                                                       time=api_event.time,
                                                       ticket_url=api_event.ticket_url)
        return release, created


class Command(BaseCommand):
    help = 'Update events for all artists. Used by cron.'

    def handle(self, *args, **options):
        artists = [artist.name for artist in
                   Artist.objects.all()]
        con = ConcertConnector()
        con.update_events(artists)