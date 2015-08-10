from models import Book, Author

from eventowl import views as baseviews
from eventowl.common_utils import normalize

from pybook.management.commands.update_releases import ReleaseConnector
from pybook.forms import UploadFileForm

from django.views.generic import FormView
from django.core.urlresolvers import reverse
from account.mixins import LoginRequiredMixin

from StringIO import StringIO
import pandas as pd


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

def _parse_csv(request):
    author_stream = StringIO(request.FILES["authors"].read())
    df = pd.read_csv(author_stream,
                     encoding='utf-8-sig')
    return set(df['authors'])

class UploadCsv(LoginRequiredMixin, FormView):
    template_name = 'pybook/upload_csv.html'
    form_class = UploadFileForm

    def form_valid(self, form):
        authors = _parse_csv(self.request)
        self.authors = authors
        _update_authors(authors, self.request.user)
        return super(UploadCsv, self).form_valid(form)

    def get_success_url(self):
        return reverse('pybook:calibre')

class AuthorsView(baseviews.OriginatorView):
    template_name = 'pybook/show_authors.html'
    context_object_name = 'authors'
    #unsubscribe_func = _unsubscribe_artist
    #favorite_func = _favorite_artist
    #unfavorite_func = _unfavorite_artist
    originator_model = Author
