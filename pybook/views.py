from models import Book, Author

from eventowl import views as baseviews
from eventowl.common_utils import normalize

from pybook.management.commands.update_releases import ReleaseConnector

class EventsView(baseviews.EventsView):
    template_name = 'pybook/show_events_table.html'
    event_model = Book
    originator_model = Author
    originator_name = 'authors'

def _update_authors(new_authors, user):
    added_authors = []
    for new_author in new_authors:
        new_author = normalize(new_author)
        author, created = Author.objects.get_or_create(name=new_author)
        if created:
            added_authors.append(new_author)
            author.save()
        author.subscribers.add(user)
    con = ReleaseConnector([user.userprofile.api_region])
    con.update_events(added_authors)

class AddAuthorsView(baseviews.AddView):
    template_name = 'pybook/add_authors.html'

    def update_func(self, *args, **kwargs):
        return _update_authors(*args, **kwargs)
