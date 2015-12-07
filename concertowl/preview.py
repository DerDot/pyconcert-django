from eventowl.app_previews import AbstractPreview
from concertowl import models


class Preview(AbstractPreview):
    
    @staticmethod
    def description():
        return "concerts close to you"
    
    @staticmethod
    def get_objects(options):
        return models.Preview.objects.all()