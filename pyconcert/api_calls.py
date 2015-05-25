from pyconcert.utils import random_string, parse_json
from eventowl.common_utils import normalize

import urllib, urllib2
from datetime import datetime
import requests
import math
from itertools import izip
import random

with open("config.json") as config_file:
    config = parse_json(config_file.read())

class Event(object):
    def __init__(self, artists, venue, city,
                 country, date, time, ticket_url):
        self.artists = artists
        self.venue = venue
        self.city = city
        self.country = country
        self.date = date
        self.time = time
        self.ticket_url = ticket_url

    def __str__(self):
        return "Event by {artists} in {venue} ({city}, {country}).".format(artists=", ".join(self.artists),
                                                                           venue=self.venue,
                                                                           city=self.city,
                                                                           country=self.country)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        for self_var, other_var in izip(vars(self), vars(other)):
            if self_var != other_var:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

def _chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

def _split_datetime(date_time):
    proper_datetime = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
    return proper_datetime.date(), proper_datetime.time()

def _get_bandsintown_events(artists, location):
    api_call = "http://api.bandsintown.com/events/search"
    args = [("location", location),
            ("format", "json"),
            ("app_id", "eventowl")]
    for artist in artists:
        args.append(("artists[]", artist))
    api_call = "%s?%s" % (api_call, urllib.urlencode(args))
    resp = parse_json(urllib.urlopen(api_call).read())
    ret = []
    if resp and not isinstance(resp, dict):
        for event in resp:
            artists = [normalize(artist["name"]) for artist in event["artists"]]
            venue = event["venue"]["name"]
            city = event["venue"]["city"]
            country = event["venue"]["country"]
            date, time = _split_datetime(event["datetime"])
            url = event["url"]
            result_event = Event(artists,
                                 venue,
                                 city,
                                 country,
                                 date,
                                 time,
                                 url)
            ret.append(result_event)
    return ret

def _normalize_inputs(artists, location):
    normalized_artists = []
    for artist in artists:
        if isinstance(artist, unicode):
            artist = artist.encode("utf8")
        normalized_artists.append(artist)

    if isinstance(location, unicode):
        location = location.encode("utf8")
    return normalized_artists, location

def _random_subset(collection, size=20):
    if len(collection) > size:
        return random.sample(collection, size)
    return collection

def recommended_artists(artists):
    api_call = 'http://api.seatgeek.com/2/recommendations/performers'
    args = [('client_id', config["SEATGEEK_ID"]),
            ('per_page', 50)]
    artists = _random_subset(artists)
    for artist in artists:
        performer_id = _seatgeek_performer_id(artist)
        if performer_id is None:
            continue
        args.append(("performers.id", performer_id))
    api_call = "%s?%s" % (api_call, urllib.urlencode(args))
    resp = parse_json(urllib.urlopen(api_call).read())
    ret = []
    for recommendation in resp['recommendations']:
        name = recommendation['performer']['name']
        genres = [genre['name'] for genre in recommendation['performer'].get('genres', [])]
        genre = ", ".join(genres)
        score = float(recommendation['score'])
        ret.append((name, genre, score))
    return ret

def _seatgeek_performer_id(artist):
    api_call = 'http://api.seatgeek.com/2/performers'
    args = [('q', artist)]
    api_call = "%s?%s" % (api_call, urllib.urlencode(args))
    resp = parse_json(urllib.urlopen(api_call).read())
    performers = resp['performers']
    if performers:
        return performers[0]['id']
    else:
        return None

def events_for_artists_bandsintown(artists, location):
    artists, location = _normalize_inputs(artists, location)
    all_events = []
    for idx, artists_chunk in enumerate(_chunks(list(artists), 50)):
        print "Working on artists number {} to {}".format(idx * 50, (idx + 1) * 50)
        events = _get_bandsintown_events(artists_chunk, location)
        for event in events:
            all_events.append(event)
    return all_events

def spotify_auth():
    state = random_string()
    api_call = "https://accounts.spotify.com/authorize"
    args = [("client_id", config["SPOTIFY_ID"]),
            ("response_type", "code"),
            ("redirect_uri", config["URL"]),
            ("scope", "user-library-read"),
            ("state", state)]
    api_call = "%s?%s" % (api_call, urllib.urlencode(args))
    return api_call, state

def spotify_token(code):
    api_call = "https://accounts.spotify.com/api/token"
    response = requests.post(api_call, data={'code': code,
                                             'grant_type':'authorization_code',
                                             'redirect_uri':config["URL"],
                                             'client_id':config["SPOTIFY_ID"],
                                             'client_secret':config["SPOTIFY_SECRET"]})
    token_info = parse_json(response.text)
    return token_info

def spotify_artists(token, limit=50):
    all_artists = set()
    base_api_call = "https://api.spotify.com/v1/me/tracks"
    iteration = 0
    while True:
        args = [("limit", limit),
                ("offset", limit * iteration)]
        api_call = "%s?%s" % (base_api_call, urllib.urlencode(args))
        request = urllib2.Request(api_call)
        request.add_header("Authorization", 'Bearer ' + token)
        response = parse_json(urllib2.urlopen(request).read())
        print "Iteration {} of {}".format(iteration + 1,
                                          int(math.ceil(response["total"] / 50.)) + 1)
        if not response["items"]:
            break
        for track in response["items"]:
            artists = track["track"]["artists"]
            for artist in artists:
                normalized_artist = normalize(artist["name"])
                all_artists.add(normalized_artist)
        iteration += 1
    return all_artists