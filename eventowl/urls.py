from django.conf.urls import patterns, url
from eventowl import views

urlpatterns = patterns('',
                       url(r"^$", views.ChoiceView.as_view(), name="choice"),
                       url(r"^impressum/$", views.ImpressumView.as_view(), name="impressum"),
                       url(r"^about/$", views.AboutView.as_view(), name="about"),
)
