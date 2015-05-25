from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       url(r'^', include('eventowl.urls', 'eventowl')),
                       url(r'^artists/', include('pyconcert.urls', 'pyconcert')),
                       url(r'^books/', include('pybook.urls', 'pybook')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^account/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
                       url(r"^account/", include("account.urls")),
)