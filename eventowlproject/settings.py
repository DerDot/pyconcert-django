"""
Django settings for pyconcertproject project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import platform
from django.conf import global_settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$#_4d0rf#(!a2dm(^=!s5h^ic(t3la6v$n)l8pp49br)19z+iq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'email_html',
    'account',
    'widget_tweaks',
    'social.apps.django_app.default',
    'debug_toolbar',
    'django_js_reverse',
    'eventowl',
    'concertowl',
    'bookowl',
    'notifications',
]

APPS_WITH_PREVIEW = (
    'concertowl',
    'bookowl',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'account.middleware.LocaleMiddleware',
    'account.middleware.TimezoneMiddleware',
    'eventowlproject.middleware.LoginRequiredMiddleware'
)

ROOT_URLCONF = 'eventowlproject.urls'

WSGI_APPLICATION = 'eventowlproject.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pyconcert',
        'USER': 'pyconcert',
        'PASSWORD': '*pyconcert*',
        'HOST': '127.0.0.1'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

TIME_ZONE = 'Europe/Berlin'

USE_TZ = False


nodename = platform.uname()[1]
IS_LOCAL = nodename != 'ip-172-31-1-209'

TEMPLATE_SETTINGS = ['IS_LOCAL']


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.core.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'account.context_processors.account'
            ],
        },
    },
]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "provided_static"),
)

ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True

PAGINATION_SIZE = 25

MAX_UPLOAD_SIZE = 2 * 1024 ** 2

EMAIL_SUBJECT_PREFIX = "[EventOwl] "
DEFAULT_FROM_EMAIL = 'mail@concertowl'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.host'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'mail@concertowl'
EMAIL_HOST_PASSWORD = 'password'

DAYS_BACK = 3

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

AUTHENTICATION_BACKENDS = ('social.backends.google.GoogleOAuth2',
                           'django.contrib.auth.backends.ModelBackend')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '644485068854-o865p7v8kb55o1u9sbskl2908tggljlp.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '61fdhJA17NI2yTRmETinqEf3'

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'eventowl.social_auth_pipeline.collect_city',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
)

SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ('city',)

LOGIN_URL = '/account/signup'
LOGIN_REDIRECT_URL = '/'

LOGIN_EXEMPT_URLS = (
     r'admin/+',
     r'account/(login|signup|password/reset)/+',
     r'account/add_profile/.*',
     r'account/confirm_email/.*',
     r'login.*',
     r'complete.*',
     r'about/+$',
     r'impressum/+$',
)

SITE_ID = 1

NUMBER_OF_PREVIEW_OBJECTS = 6

NOTIFICATIONS_USE_JSONFIELD = True

LOG_DIRECTORY = '/var/log/eventowl/'

if not IS_LOCAL:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt' : "%Y-%m-%d %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(LOG_DIRECTORY, 'eventowl.log'),
                'formatter': 'verbose'
            },
        },
        'loggers': {
            'django': {
                'handlers':['file'],
                'propagate': True,
                'level':'DEBUG',
            },
            'eventowl': {
                'handlers': ['file'],
                'level': 'DEBUG',
            },
            'bookowl': {
                'handlers': ['file'],
                'level': 'DEBUG',
            },
            'concertowl': {
                'handlers': ['file'],
                'level': 'DEBUG',
            },
        }
    }
