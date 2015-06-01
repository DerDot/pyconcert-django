from pyconcertproject import settings
from eventowl.forms import RestrictedFileField

from django import forms

class UploadFileForm(forms.Form):
    authors = RestrictedFileField(content_types=['text/csv'],
                                  max_upload_size=settings.MAX_UPLOAD_SIZE)