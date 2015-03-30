from models import Event
from tables import EventTable
from django_tables2.config import RequestConfig
from django.shortcuts import render

def show_events(request):
    table = EventTable(Event.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'pyconcert/event_table.html', {'event_table': table})