from django.conf.urls import patterns, url, include
from eventowl import views

urlpatterns = patterns('',
                       url(r"^$", views.ChoiceView.as_view(), name="choice"),
                       url(r"^impressum/$", views.ImpressumView.as_view(), name="impressum"),
                       url(r"^about/$", views.AboutView.as_view(), name="about"),
                       url(r"^account/signup/$", views.SignupView.as_view(), name="account_signup"),
                       url(r"^account/settings/$", views.SettingsView.as_view(), name="account_settings"),
                       url(r"^account/add_profile/$", views.AddProfileView.as_view(), name="account_add_profile")
)
