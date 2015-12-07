from eventowl.app_previews import AbstractPreview
from bookowl import models
from eventowlproject.settings import NUMBER_OF_PREVIEW_OBJECTS


class Preview(AbstractPreview):
    
    @staticmethod
    def description():
        return "the most popular books that will be released soon"
    
    @staticmethod
    def get_objects(options):
        return models.Preview.objects.order_by('-updated_at')[:NUMBER_OF_PREVIEW_OBJECTS]