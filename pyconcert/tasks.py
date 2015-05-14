import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyconcertproject.settings')

from celery import Celery

app = Celery('tasks', broker='amqp://localhost')
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)

from models import Artist, RecommendedArtist
from django.contrib.auth.models import User
from pyconcert import api_calls

@app.task
def spotify_artists(token):
    return api_calls.spotify_artists(token)

@app.task(ignore_result=True)
def update_recommended_artists(artists, username):
    recommended = api_calls.recommended_artists(artists)
    _add_recommendations(recommended, username)

def _add_recommendations(recommended, username):
    for artist, genre, score in recommended:
        artist = api_calls.normalize_artist(artist)
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
