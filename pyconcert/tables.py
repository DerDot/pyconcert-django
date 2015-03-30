import django_tables2 as tables
from models import Event

class EventTable(tables.Table):

    class Meta:
        model = Event
        fields = ("artist_names", "venue", "time", "date", "city", "country", "ticket_url")
        attrs = {"class": "paleblue"}
