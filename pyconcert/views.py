from models import Event
from django.views.generic import ListView

class ShowEventsView(ListView):
    model = Event