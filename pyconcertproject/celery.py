from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyconcertproject.settings')

from django.conf import settings


app = Celery('pyconcertproject', broker='amqp://localhost', backend='djcelery.backends.database:DatabaseBackend')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)
