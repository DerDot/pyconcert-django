from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^pyconcert/', include('pyconcert.urls', 'pyconcert')),
    url(r'^admin/', include(admin.site.urls)),
)