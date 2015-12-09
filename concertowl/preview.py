from eventowl.app_previews import AbstractPreview
from concertowl import models
from eventowlproject.settings import NUMBER_OF_PREVIEW_OBJECTS
from concertowl.management.commands.update_concert_preview import update_concert_preview


class Preview(AbstractPreview):
    
    @staticmethod
    def description():
        return "concerts close to you"
    
    @staticmethod
    def get_objects(options, first=True):
        city = options['city']
        country = options['country']
        previews = models.Preview.objects.filter(city=city,
                                                 country=country)
        if previews.count():
            return previews.order_by('-updated_at')[:NUMBER_OF_PREVIEW_OBJECTS]
        elif first:
            update_concert_preview(city, country)
            return Preview.get_objects(options, False)
        else:
            return []