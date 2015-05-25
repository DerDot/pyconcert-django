from django.conf.urls import patterns, url
from pybook import views

urlpatterns = patterns('',
                       url(r'^$', views.EventsView.as_view(), name='show_events'),
                       url(r'^add_authors/$', views.AddAuthorsView.as_view(), name='add_authors'),
                       url(r'^calibre/$', views.EventsView.as_view(), name='calibre'),
                       url(r'^show_authors/$', views.EventsView.as_view(), name='show_authors'),
                       url(r'^recommendations/$', views.EventsView.as_view(), name='recommendations'),
)