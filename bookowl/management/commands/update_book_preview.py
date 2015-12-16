from django.core.management.base import BaseCommand

from bookowl.models import Preview
from bookowl.api_calls import previews


class Command(BaseCommand):
    help = 'Update previews for bookowl. Used by cron.'

    def handle(self, *args, **options):
        for preview in previews():
            author = [a.title() for a in preview.authors][0]
            description = '{} by {}'.format(preview.title.title(),
                                            author)
            preview_object, created = Preview.objects.get_or_create(image=preview.image,
                                                                    description=description,
                                                                    link=preview.buy_url,
                                                                    alttext=description)
            if created:
                preview_object.save()