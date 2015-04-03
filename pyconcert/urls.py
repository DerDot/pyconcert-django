from django.conf.urls import patterns, url
from pyconcert import views

urlpatterns = patterns('',
    url(r'^$', views.show_events, name='show_events'),
    url(r'^upload$', views.upload_artists, name='upload_artists'),
    url(r'^upload_json$', views.upload_json, name='upload_json'),
)
