from datetime import date, timedelta

from django.views.generic import TemplateView
from django.views.generic import ListView
from account.mixins import LoginRequiredMixin

from pyconcertproject import settings

class ChoiceView(TemplateView):
    template_name = 'eventowl/choice.html'

class CustomListView(LoginRequiredMixin, ListView):
    paginate_by = settings.PAGINATION_SIZE

    def _filtered_and_sorted(self, name_filter, user):
        raise NotImplementedError

    def get_queryset(self):
        name_filter = self.request.GET.get("filter", "")
        return self._filtered_and_sorted(name_filter, self.request.user)

class EventsView(CustomListView):
    template_name = None
    context_object_name = 'events'
    event_model = None
    originator_model = None
    originator_name = None

    def _filtered_and_sorted(self, name_filter, user):
        subscribed_originators = self.originator_model.objects.filter(subscribers=user,
                                                                      name__icontains=name_filter)
        #kwargs = {'city__iexact': user.userprofile.city,
        oldest_shown = date.today() - timedelta(days=settings.DAYS_BACK)
        
        kwargs = {self.originator_name + '__in': subscribed_originators,
                  'date__gte': oldest_shown}
        subscribed_events = self.event_model.objects.filter(**kwargs)
        return subscribed_events.order_by("date")

class AddView(LoginRequiredMixin, TemplateView):
    template_name = None

    def get(self, request):
        add_originator = request.GET.get("add")
        if add_originator is not None:
            self.update_func([add_originator], request.user)
        return TemplateView.get(self, request)

class ImpressumView(TemplateView):
    template_name = 'eventowl/impressum.html'

class AboutView(TemplateView):
    template_name = 'eventowl/about.html'
