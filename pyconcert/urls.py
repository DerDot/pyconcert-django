from django.conf.urls import patterns, url
from pyconcert import views

urlpatterns = patterns('',
    url(r'^events_table$', views.events_table, name='events_table'),
    url(r'^upload_json$', views.upload_json, name='upload_json'),
    url(r'^spotify$', views.spotify, name='spotify'),
    url(r'^show_artists$', views.ArtistsView.as_view(), name='show_artists'),
    url(r'^$', views.EventsView.as_view(), name='show_events'),
)
