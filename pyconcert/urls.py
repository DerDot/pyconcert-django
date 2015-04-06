from django.conf.urls import patterns, url
from pyconcert import views

urlpatterns = patterns('',
    url(r'^$', views.show_events, name='show_events'),
    url(r'^upload_json$', views.upload_json, name='upload_json'),
    url(r'^spotify$', views.spotify, name='spotify'),
    url(r'^show_artists$', views.ArtistsView.as_view(), name='show_artists'),
)
