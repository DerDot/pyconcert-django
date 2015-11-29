from eventowl.app_previews import AbstractPreview
from pybook import models


class Preview(AbstractPreview):
    
    @staticmethod
    def description():
        return "the most popular books that will be released soon"
    
    @staticmethod
    def get_objects(options):
        return models.Preview.objects.all()