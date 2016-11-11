from celery import shared_task
from django.contrib.auth.models import User
from notifications.signals import notify

from .models import Artist, RecommendedArtist
from concertowl.api_calls import spotify, seatgeek
from concertowl.utils import model_helpers
from eventowl.utils.string_helpers import normalize


@shared_task
def spotify_artists(token, user):
    artists = spotify.spotify_artists(token)
    model_helpers.update_artists(artists, user)
    message = "Got {} artists from spotify.".format(len(artists))
    notify.send(user, recipient=user,
                verb=message, url_name='concertowl:show_artists')


@shared_task(ignore_result=True)
def update_recommended_artists(artists, username):
    recommended = seatgeek.recommended_artists(artists)
    _add_recommendations(recommended, username)


def _add_recommendations(recommended, username):
    for artist, genre, score in recommended:
        artist = normalize(artist)
        artist, created = Artist.objects.get_or_create(name=artist)
        if created:
            artist.genre = genre
            artist.save()

        user = User.objects.get(username=username)
        recommendation, created = RecommendedArtist.objects.get_or_create(artist=artist,
                                                                          user=user)
        if created or recommendation.score != score:
            recommendation.score = score
            recommendation.save()
