from celery import shared_task, current_task, task

from models import Artist, RecommendedArtist
from django.contrib.auth.models import User
from pyconcert import api_calls


@shared_task
def spotify_artists(token):
    return api_calls.spotify_artists(token)


@shared_task(ignore_result=True)
def update_recommended_artists(artists, username):
    recommended = api_calls.recommended_artists(artists)
    _add_recommendations(recommended, username)


def _add_recommendations(recommended, username):
    for artist, genre, score in recommended:
        artist = api_calls.normalize(artist)
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
