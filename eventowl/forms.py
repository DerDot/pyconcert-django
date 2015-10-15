from django.template.defaultfilters import filesizeformat
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User
from account import forms as account_forms

from pyconcertproject import settings


class RestrictedFileField(forms.FileField):

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.content_types.append("application/octet-stream")
        self.max_upload_size = kwargs.pop("max_upload_size")

        forms.FileField.__init__(self, *args, **kwargs)

    def clean(self, data, initial=None):
        afile = forms.FileField.clean(self, data, initial)

        try:
            content_type = afile.content_type
            if content_type in self.content_types:
                if afile._size > self.max_upload_size:
                    raise ValidationError('Please keep filesize under %s. Current filesize %s' % (filesizeformat(self.max_upload_size), filesizeformat(afile._size)))
            else:
                raise ValidationError('Filetype not supported.')
        except AttributeError:
            pass

        return data


class SignupForm(account_forms.SignupForm):
    city = forms.CharField(max_length=200)
    
    
class SocialForm(forms.Form):
    city = forms.CharField(max_length=200, required=True)
    platform = forms.ChoiceField(choices=[(name, name) for name in settings.SOCIAL_PLATFORMS.keys()])


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