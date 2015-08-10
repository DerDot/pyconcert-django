from models import Event, Artist

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, TemplateView

from account import views as account_views

from eventowl import views as baseviews
from eventowl.models import UserProfile
from eventowl.common_utils import normalize, parse_json

from pyconcert.forms import UploadFileForm, SignupForm, SettingsForm
from pyconcert.management.commands.update_events import update_events
from pyconcertproject import settings
from pyconcert.api_calls import spotify_auth, spotify_token
from pyconcert.tasks import spotify_artists, update_recommended_artists


def _update_artists(new_artists, user):
    added_artists = []
    for new_artist in new_artists:
        new_artist = normalize(new_artist)
        artist, created = Artist.objects.get_or_create(name=new_artist)
        if created:
            added_artists.append(new_artist)
            artist.save()
        artist.subscribers.add(user)
    update_events(added_artists, [user.userprofile.city])


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
                      'pyconcert/update_result.html',
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
        return render(request, 'pyconcert/spotify.html')


class EventsView(baseviews.EventsView):
    template_name = 'pyconcert/show_events_table.html'
    event_model = Event
    originator_model = Artist
    originator_name = 'artists'

    def _filtered_and_sorted(self, name_filter, user):
        pre_filtered = super(self.__class__, self)._filtered_and_sorted(name_filter, user)
        return pre_filtered.filter(city__iexact=user.userprofile.city)


def _unsubscribe_artist(artist, user):
    try:
        artist = Artist.objects.get(name=artist)
        artist.subscribers.remove(user)
        _unfavorite_artist(artist, user)
    except Artist.DoesNotExist:
        pass


def _update_recommendations(user):
    artists = [a.name for a in Artist.objects.filter(favoritedby=user)]
    update_recommended_artists.delay(artists, user.username)


def _unfavorite_artist(artist, user):
    try:
        artist = Artist.objects.get(name=artist)
        artist.favoritedby.remove(user)
        _update_recommendations(user)
    except Artist.DoesNotExist:
        pass


def _favorite_artist(artist, user):
    artist = Artist.objects.get(name=artist)
    artist.favoritedby.add(user)
    _update_recommendations(user)


class ArtistsView(baseviews.OriginatorView):
    template_name = 'pyconcert/show_artists.html'
    context_object_name = 'artists'
    unsubscribe_func = _unsubscribe_artist
    favorite_func = _favorite_artist
    unfavorite_func = _unfavorite_artist
    originator_model = Artist


class RecommendationsView(baseviews.CustomListView):
    template_name = 'pyconcert/recommendations.html'
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
    template_name = 'pyconcert/add_artists.html'

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
                          'pyconcert/update_result.html',
                          {'artists': artists_str,
                           'source': 'JSON upload'})
    else:
        form = UploadFileForm()
    return render(request,
                  'pyconcert/upload_json.html',
                  {'form': form,
                   'max_size_mb': settings.MAX_UPLOAD_SIZE / 1024 ** 2})


class SignupView(account_views.SignupView):
    form_class = SignupForm

    def after_signup(self, form):
        self.create_profile(form)
        super(SignupView, self).after_signup(form)

    def create_profile(self, form):
        profile, created = UserProfile.objects.get_or_create(user=self.created_user,
                                                             city=form.cleaned_data["city"])
        if created:
            profile.save()


class SettingsView(FormView):
    template_name = 'account/settings.html'
    form_class = SettingsForm
    success_url = '/account/settings'

    def get_initial(self):
        initial = super(SettingsView, self).get_initial()
        initial['email'] = self.request.user.email
        initial['city'] = self.request.user.userprofile.city
        return initial

    def form_valid(self, form):
        user = self.request.user
        user.email = form.cleaned_data['email']

        old_city = user.userprofile.city
        new_city = form.cleaned_data['city']
        user.userprofile.city = new_city

        user.save()
        user.userprofile.save()

        if old_city != new_city:
            subscribed_artists = [artist.name for artist in user.artists.all()]
            update_events(subscribed_artists, [new_city])

        return super(SettingsView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(SettingsView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class ToolView(TemplateView):
    template_name = 'pyconcert/tool.html'
