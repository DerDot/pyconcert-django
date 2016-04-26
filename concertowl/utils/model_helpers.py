from concertowl.management.commands.update_events import ConcertConnector
from concertowl.models import Artist
from eventowl.utils.string_helpers import normalize


def update_artists(new_artists, user):
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