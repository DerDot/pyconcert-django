from datetime import datetime, timedelta, date, time
import icalendar


def datetime_from_timestamp(timestamp):
    ts = int(timestamp)
    return datetime.fromtimestamp(ts)


def date_from_timestamp(timestamp):
    ts = int(timestamp)
    return datetime.fromtimestamp(ts).date()


def add_time_to_datetime(dt, time_obj):
    try:
        hours = time_obj.hour
        minutes = time_obj.minute
    except AttributeError:
        hours, minutes = time_obj.split(':')
        hours = int(hours)
        minutes = int(minutes)

    return datetime.combine(dt, time(hours, minutes))


def ical_event(start_date=None, start_time=None, duration=None,
               location=None, summary=None, description=None, cal=None):
    event = icalendar.Event()

    if start_date:
        if not (isinstance(start_date, datetime) or isinstance(start_date, date)):
            start_date = datetime_from_timestamp(start_date)
        if start_time:
            start_date = add_time_to_datetime(start_date, start_time)
            event.add('dtstart', start_date)

    if duration and start_date is not None:
        duration = int(duration)
        event.add('dtend', start_date + timedelta(minutes=duration))

    if summary:
        event['summary'] = summary

    if description:
        event['description'] = description

    if location:
        event['location'] = location

    event.add('dtstamp', datetime.now())

    if cal is None:
        cal = icalendar.Calendar()
    cal.add_component(event)
    return cal

