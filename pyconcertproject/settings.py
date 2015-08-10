"""
Django settings for pyconcertproject project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf import global_settings
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$#_4d0rf#(!a2dm(^=!s5h^ic(t3la6v$n)l8pp49br)19z+iq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'email_html',
    'account',
    'widget_tweaks',
    'eventowl',
    'pyconcert',
    'pybook'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "account.middleware.LocaleMiddleware",
    "account.middleware.TimezoneMiddleware",
)

ROOT_URLCONF = 'pyconcertproject.urls'

WSGI_APPLICATION = 'pyconcertproject.wsgi.application'


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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + ('django.core.context_processors.request',
                                                                             "account.context_processors.account",)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "provided_static"),
)

# Should be in application specific settings
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login'
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True

PAGINATION_SIZE = 25

MAX_UPLOAD_SIZE = 2 * 1024 ** 2

EMAIL_SUBJECT_PREFIX = "[EventOwl] "
DEFAULT_FROM_EMAIL = 'mail@pyconcert'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.host'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'mail@pyconcert'
EMAIL_HOST_PASSWORD = 'password'

DAYS_BACK = 3