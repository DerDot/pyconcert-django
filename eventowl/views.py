from datetime import date, timedelta

import os
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, FormView, View
from account import views as account_views

from eventowl.models import UserProfile, VisitorLocation
from eventowl.forms import SignupForm, SettingsForm, AddProfileForm
from eventowl.utils.dates_and_times import ical_string
from eventowl.utils.string_helpers import as_filename
from eventowlproject import settings
from eventowl import app_previews
from eventowl.utils.location import current_position
from eventowl.utils.user_agents import is_robot
from eventowl.utils.logging import get_log
from eventowlproject.settings import LOG_DIRECTORY


class ChoiceView(TemplateView):
    template_name = 'eventowl/choice.html'


class CustomListView(ListView):
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

        oldest_shown = date.today() - timedelta(days=settings.DAYS_BACK)

        kwargs = {self.originator_name + '__in': subscribed_originators,
                  'date__gte': oldest_shown}
        subscribed_events = self.event_model.objects.filter(**kwargs).distinct()
        return subscribed_events.order_by("date")


class AddView(TemplateView):
    template_name = None

    def get(self, request):
        add_originator = request.GET.get("add")
        if add_originator is not None:
            self.update_func([add_originator], request.user)
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
        context['favorites'] = self.originator_model.objects.filter(favoritedby=self.request.user)
        return context

    def _filtered_and_sorted(self, name_filter, user):
        subscribed_originators = self.originator_model.objects.filter(subscribers=user,
                                                                      name__icontains=name_filter)
        return subscribed_originators.order_by(self.order_by)

    def _update_recommendations(self, user):
        objs = [o.name for o in self.originator_model.objects.filter(favoritedby=user)]
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


class AddProfileView(FormView):
    form_class = AddProfileForm
    template_name = 'eventowl/profile.html'

    def form_valid(self, form):
        backend = self.request.session['backend']
        self.request.session['city'] = form.cleaned_data['city']
        return redirect(reverse('social:complete', args=(backend,)))

    def get(self, request):
        self.request.session['backend'] = self.request.GET.get('backend')
        return super(AddProfileView, self).get(request)


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


class LogDirectoryView(TemplateView):
    template_name = 'eventowl/log_directory.html'

    def get_context_data(self, **kwargs):
        log_names = os.listdir(LOG_DIRECTORY)
        kwargs['log_paths'] = [os.path.join(LOG_DIRECTORY, log_name) for log_name in log_names]
        return super().get_context_data(**kwargs)


class LogView(TemplateView):
    template_name = 'eventowl/log_viewer.html'

    def get_context_data(self, **kwargs):
        log_path = self.request.GET['log_path']
        log = get_log(log_path)
        kwargs['log'] = log
        return super().get_context_data(**kwargs)


class ICalView(View):
    def get(self, request):
        get_params = request.GET
        start_time = get_params.get('start_time')
        start_date = get_params.get('start_date')
        duration = get_params.get('duration')
        location = get_params.get('location')
        summary = get_params.get('summary')
        description = get_params.get('description')
        filename = as_filename(summary) + '.ics' if summary else 'cal.ics'

        istring = ical_string(start_date, start_time, duration,
                              location, summary, description)

        response = HttpResponse(istring, content_type='text/calendar')
        response['Filename'] = filename
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        return response
