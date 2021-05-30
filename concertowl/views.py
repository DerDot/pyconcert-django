from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from .models import Event, Artist, Record
from eventowl import views as baseviews
from eventowl.utils.string_helpers import parse_json
from concertowl.forms import UploadFileForm
from concertowl.utils import model_helpers
from eventowlproject import settings
from concertowl.api_calls.spotify import spotify_auth_url, spotify_token_from_code
from concertowl.tasks import spotify_artists, update_recommended_artists


def _user_events(user):
    artists = Artist.objects.filter(subscribers=user)
    events = Event.objects.filter(artists=artists).distinct()
    return events


@login_required
def spotify(request):
    if request.GET.get('import') is not None:
        auth_url, state = spotify_auth_url()
        request.session["state"] = state
        return redirect(auth_url)

    if request.GET.get('code') is not None:
        code = request.GET.get('code')
        state = request.GET.get('state')
        if request.session.get("state") != state:
            print("Oh noes...")
        token_info = spotify_token_from_code(code)
        request.session["token"] = token_info["access_token"]
        request.session["refresh_token"] = token_info["refresh_token"]
        spotify_artists.delay(token_info["access_token"])
        return render(request, 'concertowl/spotify_running.html')

    return render(request, 'concertowl/spotify.html')


class EventsView(baseviews.EventsView):
    template_name = 'concertowl/show_events_table.html'
    event_model = Event
    originator_model = Artist
    originator_name = 'artists'

    def _filtered_and_sorted(self, name_filter, user):
        pre_filtered = super(self.__class__, self)._filtered_and_sorted(
            name_filter, user)
        return pre_filtered.filter(city__iexact=user.userprofile.city)


class RecordsView(baseviews.EventsView):
    template_name = 'concertowl/show_records_table.html'
    event_model = Record
    originator_model = Artist
    originator_name = 'artists'
    override_days_back = 365


class ArtistsView(baseviews.OriginatorView):
    template_name = 'concertowl/show_artists.html'
    context_object_name = 'artists'
    update_recommendation_func = update_recommended_artists
    originator_model = Artist


class RecommendationsView(baseviews.CustomListView):
    template_name = 'concertowl/recommendations.html'
    context_object_name = 'artists'

    def get(self, request):
        new_artist = request.GET.get("new_artist")
        if new_artist is not None:
            model_helpers.update_artists([new_artist], request.user)

        return baseviews.CustomListView.get(self, request)

    def _filtered_and_sorted(self, name_filter, user):
        _recommended_artists = Artist.objects.filter(recommendedtos=user,
                                                     name__icontains=name_filter).exclude(subscribers=user)
        return _recommended_artists.order_by('-recommendation__score')


class AddArtistsView(baseviews.AddView):
    template_name = 'concertowl/add_artists.html'

    def update_func(self, *args, **kwargs):
        return model_helpers.update_artists(*args, **kwargs)


def _parse_json_file(request):
    try:
        parsed = parse_json(request.FILES["artists"].read().decode("utf8"))
    except ValueError:
        parsed = []
    return parsed


@login_required
def upload_json(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            artists = _parse_json_file(request)
            model_helpers.update_artists(artists, request.user)
            artists_str = ', '.join(sorted(artists))
            return render(request,
                          'concertowl/update_result.html',
                          {'artists': artists_str,
                           'source': 'JSON upload'})
    else:
        form = UploadFileForm()
    return render(request,
                  'concertowl/upload_json.html',
                  {'form': form,
                   'max_size_mb': settings.MAX_UPLOAD_SIZE / 1024 ** 2})


class UploadLocalView(TemplateView):
    template_name = 'concertowl/upload_local.html'
