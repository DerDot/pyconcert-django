from models import Event, Artist
from tables import EventTable
from django_tables2.config import RequestConfig
from django.shortcuts import render, redirect
from api_calls import events_for_artists_bandsintown, spotify_auth, spotify_token, spotify_artists

def _update_events():
    artists = [artist.name for artist in Artist.objects.all()]
    api_events = events_for_artists_bandsintown(artists, "Berlin")
    for api_event in api_events:
        event, created = Event.objects.get_or_create(venue=api_event.venue,
                                                     city=api_event.city,
                                                     country=api_event.country,
                                                     artists=", ".join(api_event.artists),
                                                     date=api_event.date,
                                                     time=api_event.time,
                                                     ticket_url=api_event.ticket_url)
        if created:
            event.save()

def _update_artists(new_artists):
    for new_artist in new_artists:
        artist, created = Artist.objects.get_or_create(name=new_artist)
        if created:
            artist.save()

def show_events(request):
    if(request.POST.get('update')):
        _update_events()

    if(request.POST.get('spotify')):
        token = request.session.get("token")
        token = None
        if token is None:
            auth_url, state = spotify_auth()
            request.session["state"] = state
            return redirect(auth_url)

    if(request.GET.get('code')):
        code = request.GET.get('code')
        state = request.GET.get('state')
        if request.session.get("state") != state:
            print "Oh noes..."
        token_info = spotify_token(code)
        request.session["token"] = token_info["access_token"]
        request.session["refresh_token"] = token_info["refresh_token"]
        artists = spotify_artists(token_info["access_token"])
        _update_artists(artists)

    table = EventTable(Event.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'pyconcert/event_table.html', {'event_table': table})
