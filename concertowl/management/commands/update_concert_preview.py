from django.core.management.base import BaseCommand

from concertowl.models import Preview
from concertowl.api_calls import previews
from eventowl.models import VisitorLocation


def update_concert_preview(city, country):
    for preview in previews(city, country):
        artist = [a.title() for a in preview.artists][0]
        description = '{} at {} ({})'.format(artist,
                                             preview.venue.title(),
                                             preview.date)
        preview_object, created = Preview.objects.get_or_create(image=preview.image,
                                                                description=description,
                                                                link=preview.ticket_url,
                                                                alttext=description,
                                                                city=city,
                                                                country=country)
        if created:
            preview_object.save()


class Command(BaseCommand):
    help = 'Update previews for concertowl. Used by cron.'
    
    def add_arguments(self, parser):
        parser.add_argument('--city',
                            dest='city',
                            help='City for events')
        
        parser.add_argument('--country',
                            dest='country',
                            help='Country for events')

    def handle(self, *args, **options):
        city = options.get('city')
        country = options.get('country')
        if city is None or country is None:
            locations = [(o['city'], o['country'])
                         for o in VisitorLocation.objects.values('city', 'country')]
        else:
            locations = [(city, country)]
            
        for city, country in locations:
            update_concert_preview(city, country)