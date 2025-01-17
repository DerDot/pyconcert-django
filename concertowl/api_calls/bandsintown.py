from datetime import datetime
import urllib.parse

import requests
from retrying import retry

from eventowl.utils.string_helpers import normalize, parse_json

EMPTY_IMAGE = 'https://s3.amazonaws.com/bit-photos/artistLarge.jpg'
EMPTY_THUMB = 'https://s3.amazonaws.com/bit-photos/artistThumb.jpg'


class Event(object):
    def __init__(self, artists, venue, city,
                 country, date, time, ticket_url,
                 image=None):
        self.artists = artists
        self.venue = venue
        self.city = city
        self.country = country
        self.date = date
        self.time = time
        self.ticket_url = ticket_url
        self.image = image

    def __str__(self):
        return "Event by {artists} in {venue} ({city}, {country}).".format(artists=", ".join(self.artists),
                                                                           venue=self.venue,
                                                                           city=self.city,
                                                                           country=self.country)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        for self_var, other_var in zip(vars(self), vars(other)):
            if self_var != other_var:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


def _chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def _split_datetime(date_time):
    proper_datetime = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
    return proper_datetime.date(), proper_datetime.time()


@retry(wait_exponential_multiplier=1*1000,
       wait_exponential_max=60*1000,
       stop_max_delay=240*1000)
def _call(url, args, append_args=tuple()):
    args += [("app_id", "eventowl")]

    for arg in append_args:
        url_arg = urllib.parse.quote(arg)
        url += '/{}'.format(url_arg)

    api_call = "%s?%s" % (url, urllib.parse.urlencode(args))
    resp = requests.get(api_call)
    try:
        parsed = parse_json(resp.text)
    except ValueError:
        return None

    if isinstance(parsed, dict) and 'errors' in parsed:
        message = '; '.join(parsed['errors'])
        if 'exceeded' in message:
            raise IOError(message)
        else:
            return None

    if not isinstance(parsed, list):
        print("Got malformed event for '{}'".format(url))
        return None

    return parsed


def _bandsintown_artist(name):
    url = "http://api.bandsintown.com/artists"
    args = [('api_version', '2.0')]
    append_args = [name]
    return _call(url, args, append_args)


def _get_bandsintown_events(artist, city, country=None, image=False):
    ret = []
    api_url = "https://rest.bandsintown.com/artists/{}/events/".format(
        artist.decode('utf8'))
    resp = _call(api_url, [])
    if resp:
        for event in resp:
            artists = [normalize(artist)
                       for artist in event['lineup']]
            image_url = None
            if image:
                artist = _bandsintown_artist(artists[0])
                if artist is not None:
                    image_url = artist.get('thumb_url')
            venue = normalize(event["venue"]["name"])
            event_city = normalize(event["venue"]["city"])
            if event_city != city.decode('utf8'):
                continue
            country = normalize(event["venue"]["country"])
            date, time = _split_datetime(event["datetime"])
            ticket = {}
            for offer in event.get("offers", []):
                if offer.get("type") == "Tickets":
                    ticket = offer
                    break
            event_url = event.get("url", 'http://www.bandsintown.com')
            ticket_url = ticket.get("url", event_url)
            result_event = Event(artists,
                                 venue,
                                 event_city,
                                 country,
                                 date,
                                 time,
                                 ticket_url,
                                 image_url)
            ret.append(result_event)
    return ret


def _normalize_inputs(artists, location):
    normalized_artists = []
    for artist in artists:
        if isinstance(artist, str):
            artist = artist.encode("utf8")
        normalized_artists.append(artist)

    if isinstance(location, str):
        location = location.encode("utf8")
    return normalized_artists, location


def events_for_artists_bandsintown(artists, city):
    artists, city = _normalize_inputs(artists, city)
    all_events = []
    for idx, artist in enumerate(artists):
        events = _get_bandsintown_events(artist, city)
        for event in events:
            all_events.append(event)

        if not idx % 50:
            print("Finished {} artists. Found {} events in total.".format(
                idx+1, len(all_events)))
    return all_events


def previews(city, country):
    return []
    previews = []
    print("Getting events near {} ({})".format(city, country))
    events = _get_bandsintown_events(city, country, image=True)
    for event in events:
        if event.image and event.image not in [EMPTY_IMAGE, EMPTY_THUMB]:
            previews.append(event)
    print(("Got {}".format(len(previews))))
    return previews
