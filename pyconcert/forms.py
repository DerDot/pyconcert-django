from django import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from pyconcertproject import settings

class RestrictedFileField(forms.FileField):

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
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

class UploadFileForm(forms.Form):
    artists = RestrictedFileField(content_types=settings.CONTENT_TYPES,
                                max_upload_size=settings.MAX_UPLOAD_SIZE)