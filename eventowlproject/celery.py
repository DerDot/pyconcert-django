import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventowlproject.settings')

from django.conf import settings

BROKER_URL = os.environ.get('REDIS_URL', 'localhost')

app = Celery('eventowlproject', broker=BROKER_URL,
             backend='djcelery.backends.database:DatabaseBackend')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    BROKER_URL=BROKER_URL,
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)
