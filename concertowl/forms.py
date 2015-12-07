from eventowlproject import settings
from eventowl.forms import RestrictedFileField

from django import forms

class UploadFileForm(forms.Form):
    artists = RestrictedFileField(content_types=['application/json'],
                                  max_upload_size=settings.MAX_UPLOAD_SIZE)