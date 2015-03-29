from django.conf.urls import patterns, url
from pyconcert import views 

urlpatterns = patterns('',
    url(r'^$', views.ShowEventsView.as_view(), name='show_events'),
)