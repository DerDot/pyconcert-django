from django.core.management.base import BaseCommand

from eventowl.utils.common_functions import EventConnector
from eventowl.utils.django_helpers import set_if_different, set_if_smaller
from bookowl.models import Book, Author
from bookowl.api_calls import book_releases



class ReleaseConnector(EventConnector):
    originator_name = 'authors'
    originator_model = Author

    def _get_events(self, authors):
        return book_releases(authors)

    def _get_or_create_object(self, api_release):
        exists = Book.objects.filter(title=api_release.title).exists()
        if exists:
            release = Book.objects.get(title=api_release.title)
            newer = set_if_smaller(release, 'date', api_release.date)
            if newer:
                set_if_different(release, 'buy_url', api_release.buy_url)
                set_if_different(release, 'isbn', api_release.isbn)
            should_save = newer

        else:
            release = Book.objects.create(title=api_release.title,
                                          isbn=api_release.isbn,
                                          date=api_release.date,
                                          buy_url=api_release.buy_url)
            should_save = True

        return release, should_save
    
    def _message_for_originator(self, author):
        return "New book by {}".format(author.name.title())

    def _name_for_originator(self, author):
        return author.name.lower()
    
    @staticmethod
    def _url_name():
        return 'bookowl:show_events'

    @staticmethod
    def _description(release):
        return "The book's title is {} and it's going to be released on {}.".format(release.title.title(), release.date)

    @staticmethod
    def _should_notify(user, event):
        return True


class Command(BaseCommand):
    help = 'Update book releases for all authors. Used by cron.'

    def handle(self, *args, **options):
        authors = [author.name for author in
                   Author.objects.all()]
        con = ReleaseConnector()
        con.update_events(authors)
