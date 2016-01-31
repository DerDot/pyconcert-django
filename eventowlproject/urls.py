from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout
from notifications import urls as notification_urls

urlpatterns = [
    url(r'^', include('eventowl.urls', 'eventowl')),
    url(r'^artists/', include('concertowl.urls', 'concertowl')),
    url(r'^books/', include('bookowl.urls', 'bookowl')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/logout/$', logout, {'next_page': '/'}),
    url(r'^account/', include('account.urls')),
    url('^inbox/notifications/', include(notification_urls)),
    url('', include('social.apps.django_app.urls', 'social')),
]