from models import Event, Artist, UserProfile

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, FormView, TemplateView

from account import views as account_views

from pyconcert.forms import UploadFileForm, SignupForm, SettingsForm
from pyconcert.management.commands.update_events import update_events
from pyconcertproject import settings
from api_calls import spotify_auth, spotify_token, spotify_artists
import utils
from account.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect

def _update_artists(new_artists, user):
    added_artists = []
    for new_artist in new_artists:
        new_artist = unicode(new_artists).decode("utf8").lower()
        artist, created = Artist.objects.get_or_create(name=new_artist)
        if created:
            added_artists.append(new_artist)
            artist.save()
        artist.subscribers.add(user)
    update_events(added_artists)

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
        artists = spotify_artists(token_info["access_token"])
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

class CustomListView(LoginRequiredMixin, ListView):
    paginate_by = settings.PAGINATION_SIZE

    def _filtered_and_sorted(self, name_filter, user):
        raise NotImplementedError

    def get_queryset(self):
        name_filter = self.request.GET.get("filter", "")
        return self._filtered_and_sorted(name_filter, self.request.user)

class EventsView(CustomListView):
    template_name = 'pyconcert/show_events_table.html'
    context_object_name = 'events'

    def _filtered_and_sorted(self, name_filter, user):
        subscribed_artists = Artist.objects.filter(subscribers=user,
                                                   name__icontains=name_filter)
        subscribed_events = Event.objects.filter(artists__in=subscribed_artists)
        return subscribed_events.order_by("date")

def _unsubscribe_artist(artist, user):
    try:
        artist = Artist.objects.get(name=artist)
        artist.subscribers.remove(user)
    except Artist.DoesNotExist:
        pass

class ArtistsView(CustomListView):
    template_name = 'pyconcert/show_artists.html'
    context_object_name = 'artists'

    def get(self, request):
        unsubscribe = request.GET.get("remove")
        if unsubscribe is not None:
            _unsubscribe_artist(unsubscribe, request.user)
        return CustomListView.get(self, request)

    def _filtered_and_sorted(self, name_filter, user):
        subscribed_artists = Artist.objects.filter(subscribers=user,
                                                   name__icontains=name_filter)
        return subscribed_artists.order_by("name")

class AddArtistsView(LoginRequiredMixin, TemplateView):
    template_name = 'pyconcert/add_artists.html'

    def get(self, request):
        add_artist = request.GET.get("add")
        if add_artist is not None:
            _update_artists(add_artist, request.user)
        return TemplateView.get(self, request)

def _parse_json_file(request):
    try:
        parsed = utils.parse_json(request.FILES["artists"].read())
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
                          {'artists':artists_str,
                           'source':'JSON upload'})
    else:
        form = UploadFileForm()
    return render(request,
                  'pyconcert/upload_json.html',
                  {'form':form})

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
        user_profile = user.userprofile
        user_profile.city = form.cleaned_data['city']
        user.save()
        user_profile.save()
        return super(SettingsView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(SettingsView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs