from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from models import Event, Artist
from eventowl import views as baseviews
from eventowl.utils.string_helpers import normalize, parse_json
from concertowl.forms import UploadFileForm
from concertowl.management.commands.update_events import ConcertConnector
from eventowlproject import settings
from concertowl.api_calls import spotify_auth, spotify_token
from concertowl.tasks import spotify_artists, update_recommended_artists


def _update_artists(new_artists, user):
    added_artists = []
    for new_artist in new_artists:
        new_artist = normalize(new_artist)
        artist, created = Artist.objects.get_or_create(name=new_artist)
        if created:
            added_artists.append(new_artist)
            artist.save()
        artist.subscribers.add(user)
    con = ConcertConnector()
    con.update_events(added_artists, cities=[user.userprofile.city])


def _user_events(user):
    artists = Artist.objects.filter(subscribers=user)
    events = Event.objects.filter(artists=artists).distinct()
    return events


@login_required
def spotify(request):
    if request.GET.get('code') is not None:
        code = request.GET.get('code')
        state = request.GET.get('state')
        if request.session.get("state") != state:
            print "Oh noes..."
        token_info = spotify_token(code)
        request.session["token"] = token_info["access_token"]
        request.session["refresh_token"] = token_info["refresh_token"]
        task = spotify_artists.delay(token_info["access_token"])
        artists = task.get()
        _update_artists(artists, request.user)
        artists_str = ', '.join(sorted(artists))
        return render(request,
                      'concertowl/update_result.html',
                      {'artists':artists_str,
                       'source':'Spotify'})

    elif request.GET.get('import') is not None:
        token = request.session.get("token")
        token = None
        if token is None:
            auth_url, state = spotify_auth()
            request.session["state"] = state
            return redirect(auth_url)
    else:
        return render(request, 'concertowl/spotify.html')


class EventsView(baseviews.EventsView):
    template_name = 'concertowl/show_events_table.html'
    event_model = Event
    originator_model = Artist
    originator_name = 'artists'

    def _filtered_and_sorted(self, name_filter, user):
        pre_filtered = super(self.__class__, self)._filtered_and_sorted(name_filter, user)
        return pre_filtered.filter(city__iexact=user.userprofile.city)


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
            _update_artists([new_artist], request.user)

        return baseviews.CustomListView.get(self, request)

    def _filtered_and_sorted(self, name_filter, user):
        _recommended_artists = Artist.objects.filter(recommendedtos=user,
                                                    name__icontains=name_filter).exclude(subscribers=user)
        return _recommended_artists.order_by('-recommendation__score')


class AddArtistsView(baseviews.AddView):
    template_name = 'concertowl/add_artists.html'

    def update_func(self, *args, **kwargs):
        return _update_artists(*args, **kwargs)


def _parse_json_file(request):
    try:
        parsed = parse_json(request.FILES["artists"].read())
    except ValueError:
        parsed = []
    return parsed


@login_required
def upload_json(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            artists = _parse_json_file(request)
            _update_artists(artists, request.user)
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

class ToolView(TemplateView):
    template_name = 'concertowl/tool.html'
