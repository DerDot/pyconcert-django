from abc import ABCMeta, abstractmethod

from notifications import notify


class EventConnector(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def _get_events(self, originators):
        pass

    @abstractmethod
    def _get_or_create_object(self, api_event):
        pass
    
    @abstractmethod
    def _message_for_originator(self, db_originator):
        pass

    def update_events(self, originators, **kwargs):
        api_events = self._get_events(originators, **kwargs)
        for api_event in api_events:
            event, should_save = self._get_or_create_object(api_event)
            if should_save:
                event.save()

            for db_originator in self._db_originators(api_event):
                getattr(event, self.originator_name).add(db_originator)
                if should_save:
                    self._notify_subscribers(db_originator)

    def _db_originators(self, api_event):
        originators = []
        for event_originator in getattr(api_event, self.originator_name):
            originator, created = self.originator_model.objects.get_or_create(name=event_originator)
            if created:
                originator.save()
            originators.append(originator)
        return originators
    
    def _notify_subscribers(self, db_originator):
        for user in db_originator.subscribers.all():
            message = self._message_for_originator(db_originator)
            notify.send(user, recipient=user,
                        verb=message)