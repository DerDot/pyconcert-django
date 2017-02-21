from django.core.management.base import BaseCommand

from concertowl.api_calls.discogs import records_for_artists
from concertowl.models import Artist, Record
from eventowl.utils.common_functions import EventConnector


class RecordConnector(EventConnector):
    originator_name = 'artists'
    originator_model = Artist

    def _get_events(self, artists):
        print("Getting new records...")
        return records_for_artists(artists)

    def _get_or_create_object(self, api_event):
        release, created = Record.objects.get_or_create(
            title=api_event.title,
            date=api_event.release_date,
            details_url=api_event.url
        )
        return release, created
    
    def _message_for_originator(self, artist):
        return "New record by {}".format(artist.name.title())

    def _name_for_originator(self, artist):
        return artist.name.lower()
    
    @staticmethod
    def _url_name():
        return 'concertowl:show_records'

    @staticmethod
    def _description(event):
        return "This record titled {title} will be released on {date}.".format(
            title=event.title.title(),
            date=event.date
        )

    @staticmethod
    def _should_notify(user, event):
        return True


class Command(BaseCommand):
    help = 'Update records for all artists. Used by cron.'

    def handle(self, *args, **options):
        artists = [artist.name for artist in
                   Artist.objects.all()]
        con = RecordConnector()
        con.update_events(artists)