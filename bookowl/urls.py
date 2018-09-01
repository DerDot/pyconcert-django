from django.conf.urls import url
from bookowl import views

app_name = 'bookowl'

urlpatterns = [
    url(r'^$', views.EventsView.as_view(), name='show_events'),
    url(r'^add_authors/$', views.AddAuthorsView.as_view(), name='add_authors'),
    url(r'^calibre/$', views.UploadCsv.as_view(), name='calibre'),
    url(r'^show_authors/$', views.AuthorsView.as_view(), name='show_authors'),
    url(r'^recommendations/$', views.EventsView.as_view(), name='recommendations'),
]
