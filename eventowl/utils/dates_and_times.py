from datetime import datetime, timedelta
import icalendar


def datetime_from_timestamp(timestamp):
    ts = int(timestamp)
    return datetime.fromtimestamp(ts)


def date_from_timestamp(timestamp):
    ts = int(timestamp)
    return datetime.fromtimestamp(ts).date()


def add_time_to_datetime(dt, time_string):
    hours, minutes = time_string.split(':')
    return dt.replace(hour=int(hours), minute=int(minutes))


def ical_string(start_date=None, start_time=None, duration=None,
                location=None, summary=None, description=None):
    event = icalendar.Event()

    start_dt = None
    if start_date:
        if start_time:
            start_dt = datetime_from_timestamp(start_date)
            start_dt = add_time_to_datetime(start_dt, start_time)
            event.add('dtstart', start_dt)
        else:
            event.add('dtstart', date_from_timestamp(start_date))

    if duration and start_dt is not None:
        duration = int(duration)
        event.add('dtend', start_dt + timedelta(minutes=duration))

    if summary:
        event['summary'] = summary

    if description:
        event['description'] = description

    if location:
        event['location'] = location

    event.add('dtstamp', datetime.now())

    cal = icalendar.Calendar()
    cal.add_component(event)
    return cal.to_ical()

