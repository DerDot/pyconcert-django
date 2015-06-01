from pyconcertproject import settings
from eventowl.forms import RestrictedFileField

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from account import forms as account_forms

class SignupForm(account_forms.SignupForm):
    city = forms.CharField(max_length=200)

class SettingsForm(forms.Form):
    city = forms.CharField(max_length=200)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(SettingsForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()
        email = cleaned_data.get("email")
        if (email.lower() != self.user.email.lower() and
            User.objects.filter(email__iexact=email).exists()):
            raise ValidationError('E-mail already in use.')
        return cleaned_data

class UploadFileForm(forms.Form):
    artists = RestrictedFileField(content_types=['application/json'],
                                  max_upload_size=settings.MAX_UPLOAD_SIZE)