import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ["DEBUG"] == "True"

ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(',')

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
    'social_django',
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

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'account.middleware.LocaleMiddleware',
    'account.middleware.TimezoneMiddleware',
    'eventowlproject.middleware.LoginRequiredMiddleware'
]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
    SECURE_SSL_REDIRECT = True
    MIDDLEWARE_CLASSES.insert(0, 'django.middleware.security.SecurityMiddleware')

ROOT_URLCONF = 'eventowlproject.urls'

WSGI_APPLICATION = 'eventowlproject.wsgi.application'

DATABASES = {'default': dj_database_url.config()}

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
TIME_ZONE = 'Europe/Berlin'
USE_TZ = False

IS_LOCAL = os.environ['IS_LOCAL'] == "True"

TEMPLATE_SETTINGS = ['IS_LOCAL', 'MAX_UPLOAD_SIZE_MB']

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
                'django.template.context_processors.request',
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

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True

PAGINATION_SIZE = 100

MAX_UPLOAD_SIZE_MB = 2
MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE_MB * 1024 ** 2

EMAIL_SUBJECT_PREFIX = "[EventOwl] "
DEFAULT_FROM_EMAIL = "eventowl@" +  os.environ['SPARKPOST_SANDBOX_DOMAIN']

EMAIL_USE_TLS = True
EMAIL_HOST = os.environ['SPARKPOST_SMTP_HOST']
EMAIL_PORT = int(os.environ['SPARKPOST_SMTP_PORT'])
EMAIL_HOST_USER = os.environ['SPARKPOST_SMTP_USERNAME']
EMAIL_HOST_PASSWORD = os.environ['SPARKPOST_SMTP_PASSWORD']

DAYS_BACK = 3

AUTHENTICATION_BACKENDS = ('social_core.backends.google.GoogleOAuth2',
                           'django.contrib.auth.backends.ModelBackend')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ["SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"]
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ["SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"]

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'eventowl.social_auth_pipeline.collect_city',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
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
     r'feed/.*',
     r'calendar/.*'
)

SITE_ID = 1

NUMBER_OF_PREVIEW_OBJECTS = 6

NOTIFICATIONS_USE_JSONFIELD = True

WHITENOISE_ROOT = 'provided_static/icons/favicons/'

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
            },
        },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
            },
        }
    }
