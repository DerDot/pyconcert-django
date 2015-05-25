from django.core.management.base import BaseCommand

from eventowl.common_utils import EventConnector

from pybook.models import Book, Author
from pybook.api_calls import book_releases

class ReleaseConnector(EventConnector):
    originator_name = 'authors'
    originator_model = Author
    location_name = 'api_region'

    def _get_event(self, authors, region):
        return book_releases(authors, region)

    def _get_or_create_object(self, api_release):
        release, created = Book.objects.get_or_create(title=api_release.venue,
                                                      isbn=api_release.city,
                                                      date=api_release.country,
                                                      buy_url=api_release.date)
        return release, created

class Command(BaseCommand):
    help = 'Update book releases for all authors. Used by cron.'

    def handle(self, *args, **options):
        authors = [author.name for author in
                   Author.objects.all()]
        con = ReleaseConnector()
        con.update_events(authors)
