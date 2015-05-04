import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyconcertproject.settings')

from celery import Celery

app = Celery('tasks', broker='amqp://localhost')
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)

from pyconcert import api_calls

@app.task
def spotify_artists(token):
    return api_calls.spotify_artists(token)