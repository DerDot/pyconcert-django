release: python3 manage.py migrate --noinput
web: gunicorn eventowlproject.wsgi --log-file - -c serverconf/gunicorn.conf
worker: celery -A eventowlproject worker