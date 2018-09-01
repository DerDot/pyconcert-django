from django.conf.urls import url
from eventowl import views

app_name = 'eventowl'

urlpatterns = [
    url(r"^$", views.ChoiceView.as_view(), name="choice"),
    url(r"^impressum/$", views.ImpressumView.as_view(), name="impressum"),
    url(r"^about/$", views.AboutView.as_view(), name="about"),
    url(r"^ical/$", views.ICalView.as_view(), name="ical"),
    url(r"^account/signup/$", views.SignupView.as_view(), name="account_signup"),
    url(r"^account/settings/$", views.SettingsView.as_view(), name="account_settings"),
    url(r"^account/add_profile/$", views.AddProfileView.as_view(),
        name="account_add_profile"),
    url(r'^feed/(?P<uuid>[\da-f-]+)/$',
        views.NotificationsFeed(), name="feed"),
    url(r'^calendar/(?P<uuid>[\da-f-]+)/$',
        views.CalendarView.as_view(), name="calendar"),
]
