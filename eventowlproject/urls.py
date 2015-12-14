from django.conf.urls import patterns, include, url
from django.contrib import admin
import notifications

urlpatterns = patterns('',
                       url(r'^', include('eventowl.urls', 'eventowl')),
                       url(r'^artists/', include('concertowl.urls', 'concertowl')),
                       url(r'^books/', include('bookowl.urls', 'bookowl')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^account/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
                       url(r'^account/', include('account.urls')),
                       url('^inbox/notifications/', include(notifications.urls)),
                       url('', include('social.apps.django_app.urls', 'social')),
)