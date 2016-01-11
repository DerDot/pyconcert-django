from django.conf.urls import url
from eventowl import views
from django.contrib.auth.decorators import user_passes_test

urlpatterns = [url(r"^$", views.ChoiceView.as_view(), name="choice"),
               url(r"^impressum/$", views.ImpressumView.as_view(), name="impressum"),
               url(r"^about/$", views.AboutView.as_view(), name="about"),
               url(r"^logs/$", user_passes_test(lambda u: u.is_superuser)(views.LogView.as_view()), name="log"),
               url(r"^account/signup/$", views.SignupView.as_view(), name="account_signup"),
               url(r"^account/settings/$", views.SettingsView.as_view(), name="account_settings"),
               url(r"^account/add_profile/$", views.AddProfileView.as_view(), name="account_add_profile")
               ]
