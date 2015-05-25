from eventowl.models import UserProfile

class EventConnector(object):

    def __init__(self, locations=None):
        if locations is None:
            locations = self._all_locations()

    def _get_event(self, *args, **kwargs):
        raise NotImplementedError

    def _get_or_create_object(self, api_event):
        raise NotImplementedError

    def update_events(self, originators):
        for location in self.locations:
            print "Updating events for", location
            api_events = self._get_event(originators, location)
            for api_event in api_events:
                event, created = self._get_or_create_object(api_event)
                if created:
                    event.save()
                for db_originator in self._db_originators(api_event):
                    event.get(self.originator_name).add(db_originator)

    def _db_originators(self, api_event):
        originators = []
        for event_originator in api_event.get(self.originator_name):
            originator, created = self.originator_model.objects.get_or_create(name=event_originator)
            if created:
                originator.save()
            originators.append(originator)
        return originators

    def _all_locations(self):
        locations = set()
        for user_profile in UserProfile.objects.all():
            locations.add(user_profile.get(self.location_name))
        return locations


def normalize(name):
    if isinstance(name, unicode):
        name = name.encode("utf8")
    return name.lower()
