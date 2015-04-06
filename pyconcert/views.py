from models import Event, Artist
from tables import EventTable
from django_tables2.config import RequestConfig
from django.shortcuts import render, redirect
from api_calls import spotify_auth, spotify_token, spotify_artists
import utils
from django.contrib.auth.decorators import login_required
from pyconcert.forms import UploadFileForm

def _update_artists(new_artists, user):
    for new_artist in new_artists:
        new_artists = unicode(new_artists).decode("utf8").lower()
        artist, created = Artist.objects.get_or_create(name=new_artist)
        if created:
            artist.save()
        artist.subscribers.add(user)
        
def _user_events(user):
    artists = Artist.objects.filter(subscribers=user)
    events = Event.objects.filter(artists=artists).distinct()
    return events

@login_required
def spotify(request):
    if(request.GET.get('code')):
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
    else:
        token = request.session.get("token")
        token = None
        if token is None:
            auth_url, state = spotify_auth()
            request.session["state"] = state
            return redirect(auth_url)

@login_required
def show_events(request):
    table = EventTable(_user_events(request.user))
    RequestConfig(request).configure(table)
    return render(request,
                  'pyconcert/event_table.html',
                  {'event_table':table})

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
