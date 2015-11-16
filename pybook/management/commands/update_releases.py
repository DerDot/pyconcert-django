from django.core.management.base import BaseCommand

from eventowl.utils.common_functions import EventConnector
from eventowl.utils.django_helpers import set_if_different
from pybook.models import Book, Author
from pybook.api_calls import book_releases



class ReleaseConnector(EventConnector):
    originator_name = 'authors'
    originator_model = Author

    def _get_events(self, authors):
        return book_releases(authors)

    def _get_or_create_object(self, api_release):
        exists = Book.objects.filter(title=api_release.title,
                                     isbn=api_release.isbn).exists()
        if exists:
            release = Book.objects.get(title=api_release.title,
                                       isbn=api_release.isbn)
            should_save = set_if_different(release, 'date', api_release.date)
            should_save |= set_if_different(release, 'buy_url', api_release.buy_url)
        else:
            release = Book.objects.create(title=api_release.title,
                                          isbn=api_release.isbn,
                                          date=api_release.date,
                                          buy_url=api_release.buy_url)
            should_save = True

        return release, should_save


class Command(BaseCommand):
    help = 'Update book releases for all authors. Used by cron.'

    def handle(self, *args, **options):
        authors = [author.name for author in
                   Author.objects.all()]
        con = ReleaseConnector()
        con.update_events(authors)
