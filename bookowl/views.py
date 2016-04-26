import csv
from io import StringIO

from django.views.generic import FormView
from django.core.urlresolvers import reverse

from .models import Book, Author
from eventowl import views as baseviews
from eventowl.utils.string_helpers import normalize
from bookowl.management.commands.update_releases import ReleaseConnector
from bookowl.forms import UploadFileForm
from bookowl.tasks import update_recommended_authors


class EventsView(baseviews.EventsView):
    template_name = 'bookowl/show_events_table.html'
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
    con = ReleaseConnector()
    con.update_events(added_authors)


class AddAuthorsView(baseviews.AddView):
    template_name = 'bookowl/add_authors.html'

    def update_func(self, *args, **kwargs):
        return _update_authors(*args, **kwargs)


def _parse_csv(request):
    author_stream = StringIO(request.FILES["authors"].read().decode('utf-8-sig'))
    reader = csv.DictReader(author_stream, delimiter=';')
    try:
        authors = {row['authors'] for row in reader}
    except KeyError:
        authors = set()
    return authors


class UploadCsv(FormView):
    template_name = 'bookowl/upload_csv.html'
    form_class = UploadFileForm

    def form_valid(self, form):
        authors = _parse_csv(self.request)
        self.authors = authors
        _update_authors(authors, self.request.user)
        return super(UploadCsv, self).form_valid(form)

    def get_success_url(self):
        return reverse('bookowl:calibre')


class AuthorsView(baseviews.OriginatorView):
    template_name = 'bookowl/show_authors.html'
    context_object_name = 'authors'
    update_recommendation_func = update_recommended_authors
    originator_model = Author
