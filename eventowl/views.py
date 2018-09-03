from datetime import date, timedelta

import icalendar
import notifications
from django.contrib.syndication.views import Feed
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, FormView, View
from account import views as account_views

from concertowl.models import Event, Artist
from eventowl.models import UserProfile, VisitorLocation
from eventowl.forms import SignupForm, SettingsForm
from eventowl.utils.dates_and_times import ical_event
from eventowl.utils.string_helpers import as_filename
from eventowlproject import settings
from eventowl import app_previews
from eventowl.utils.location import current_position
from eventowl.utils.user_agents import is_robot
from eventowlproject.settings import DATABASES


class ChoiceView(TemplateView):
    template_name = 'eventowl/choice.html'


class CustomListView(ListView):
    paginate_by = settings.PAGINATION_SIZE

    def _filtered_and_sorted(self, name_filter, user):
        raise NotImplementedError

    def get_queryset(self):
        name_filter = self.request.GET.get("name_filter", "")
        return self._filtered_and_sorted(name_filter, self.request.user)


def _subscribed_events(originator_model, originator_name, event_model, user, name_filter='', override_days_back=None):
    subscribed_originators = originator_model.objects.filter(subscribers=user,
                                                             name__icontains=name_filter)

    days_back = override_days_back if override_days_back is not None else settings.DAYS_BACK
    oldest_shown = date.today() - timedelta(days=days_back)

    kwargs = {originator_name + '__in': subscribed_originators,
              'date__gte': oldest_shown}
    subscribed_events = event_model.objects.filter(**kwargs).distinct()
    return subscribed_events.order_by("date").distinct()


class EventsView(CustomListView):
    template_name = None
    context_object_name = 'events'
    event_model = None
    originator_model = None
    originator_name = None
    override_days_back = None

    def _filtered_and_sorted(self, name_filter, user):
        return _subscribed_events(self.originator_model, self.originator_name, self.event_model,
                                  user, name_filter, self.override_days_back)


class AddView(TemplateView):
    template_name = None

    def get(self, request):
        add_originator = request.GET.get('add')
        if add_originator is not None:
            self.update_func(add_originator.split(','), request.user)
        return TemplateView.get(self, request)


class OriginatorView(CustomListView):
    template_name = None
    context_object_name = None
    originator_model = None
    order_by = 'name'

    def get(self, request):
        unsubscribe = request.GET.get("remove")
        if unsubscribe is not None:
            self._unsubscribe(unsubscribe, request.user)

        favorite = request.GET.get("favorite")
        if favorite is not None:
            self._favorite(favorite, request.user)

        unfavorite = request.GET.get("unfavorite")
        if unfavorite is not None:
            self._unfavorite(unfavorite, request.user)

        return CustomListView.get(self, request)

    def get_context_data(self, **kwargs):
        context = CustomListView.get_context_data(self, **kwargs)
        context['favorites'] = self.originator_model.objects.filter(
            favoritedby=self.request.user)
        return context

    def _filtered_and_sorted(self, name_filter, user):
        subscribed_originators = self.originator_model.objects.filter(subscribers=user,
                                                                      name__icontains=name_filter)
        return subscribed_originators.order_by(self.order_by)

    def _update_recommendations(self, user):
        objs = [o.name for o in self.originator_model.objects.filter(
            favoritedby=user)]
        self.update_recommendation_func.delay(objs, user.username)

    def _unfavorite(self, originator, user):
        try:
            obj = self.originator_model.objects.get(name=originator)
            obj.favoritedby.remove(user)
            self._update_recommendations(user)
        except self.originator_model.DoesNotExist:
            pass

    def _unsubscribe(self, originator, user):
        try:
            obj = self.originator_model.objects.get(name=originator)
            obj.subscribers.remove(user)
            self._unfavorite(originator, user)
        except self.originator_model.DoesNotExist:
            pass

    def _favorite(self, originator, user):
        obj = self.originator_model.objects.get(name=originator)
        obj.favoritedby.add(user)
        self._update_recommendations(user)


class ImpressumView(TemplateView):
    template_name = 'eventowl/impressum.html'


class AboutView(TemplateView):
    template_name = 'eventowl/about.html'


def _get_location(request):
    city, country = current_position(request)
    if city is None and country is None:
        city = 'new york'
        country = 'new york'

    return city, country


def _save_location(city, country, request):
    if not is_robot(request):
        VisitorLocation.objects.update_or_create(city=city,
                                                 country=country)


class SignupView(account_views.SignupView):
    form_class = SignupForm

    def get_context_data(self, **kwargs):
        city, country = _get_location(self.request)
        _save_location(city, country, self.request)

        kwargs['previews'] = app_previews.get_all_objects({'city': city,
                                                           'country': country})
        return super(SignupView, self).get_context_data(**kwargs)

    def after_signup(self, form):
        self.create_profile(form)
        super(SignupView, self).after_signup(form)

    def create_profile(self, form):
        UserProfile.objects.update_or_create(user=self.created_user,
                                             city=form.cleaned_data["city"])


class SettingsView(FormView):
    template_name = 'account/settings.html'
    form_class = SettingsForm
    success_url = '/account/settings'

    def get_initial(self):
        initial = super(SettingsView, self).get_initial()
        initial['email'] = self.request.user.email
        initial['city'] = self.request.user.userprofile.city
        return initial

    def form_valid(self, form):
        user = self.request.user
        user.email = form.cleaned_data['email']

        old_city = user.userprofile.city
        new_city = form.cleaned_data['city']
        user.userprofile.city = new_city

        user.save()
        user.userprofile.save()

        if old_city != new_city:
            subscribed_artists = [artist.name for artist in user.artists.all()]
            # update_events(subscribed_artists, [new_city]) TODO: do in subclass

        return super(SettingsView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(SettingsView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class ICalView(View):
    def get(self, request):
        get_params = request.GET
        start_time = get_params.get('start_time')
        start_date = get_params.get('start_date')
        duration = get_params.get('duration')
        whole_day = get_params.get('whole_day') == '1'
        location = get_params.get('location')
        summary = get_params.get('summary')
        description = get_params.get('description')
        filename = as_filename(summary) + '.ics' if summary else 'cal.ics'
        istring = ical_event(start_date, start_time, duration, location,
                             summary, description, whole_day=whole_day).to_ical()

        response = HttpResponse(istring, content_type='text/calendar')
        response['Filename'] = filename
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            filename)
        return response


class NotificationsFeed(Feed):
    title = "Whats new on eventowl"
    link = '/feed/'
    description = "All your new concerts, book releases and everything else."

    def get_object(self, request, uuid):
        return UserProfile.objects.get(uuid=uuid).user

    def items(self, obj):
        return notifications.models.Notification.objects.filter(recipient=obj).order_by('-timestamp')

    def item_title(self, item):
        return item.verb

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        url_name = item.data.get('url_name')
        return url_name


class CalendarView(View):
    def get(self, request, uuid):
        user = UserProfile.objects.get(uuid=uuid).user
        db_events = _subscribed_events(Artist, 'artists', Event, user).filter(
            city__iexact=user.userprofile.city)
        if 'postgres_disabled' in DATABASES['default']['ENGINE']:
            events = db_events.order_by(
                'date', 'time', 'venue').distinct('date', 'time', 'venue')
        else:
            seen = set()
            events = []
            for event in db_events:
                key = (event.date, event.time, event.venue)
                if key not in seen:
                    events.append(event)
                    seen.add(key)

        cal = icalendar.Calendar()
        for event in events:
            location = "{}, {}".format(event.venue.title(), event.city.title())
            summary = ", ".join(artist.name.title()
                                for artist in event.artists.all())
            duration = 120
            description = ""
            cal = ical_event(event.date, event.time, duration,
                             location, summary, description, cal)

        filename = 'events.ics'
        response = HttpResponse(cal.to_ical(), content_type='text/calendar')
        response['Filename'] = filename
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            filename)
        return response
