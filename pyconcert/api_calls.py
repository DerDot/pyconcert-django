import urllib, urllib2
from datetime import datetime
from pyconcert.utils import random_string, parse_json
import requests
import math

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
        return "Event by {artists} in {venue} ({city}, {country}).".format(artists=u", ".join(self.artists),
                                                                           venue=self.venue,
                                                                           city=self.city,
                                                                           country=self.country)
 
    def __repr__(self):
        return self.__str__()

def _chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

def _split_datetime(date_time):
    proper_datetime = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
    return proper_datetime.date(), proper_datetime.time()

def _normalize_artist(artist_name):
    return artist_name.encode("utf8").lower()

def _get_bandsintown_events(artists, location):
    api_call = "http://api.bandsintown.com/events/search"
    args = [("location", location),
            ("format", "json"),
            ("app_id", "pyconcert")]
    for artist in artists:
        args.append(("artists[]", artist.encode("utf8")))
    api_call = "%s?%s" % (api_call, urllib.urlencode(args))
    resp = parse_json(urllib.urlopen(api_call).read())
    ret = []
    for event in resp:
        artists = [_normalize_artist(artist) for artist in event["artists"]]
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

def events_for_artists_bandsintown(artists, location):
    all_events = []
    for artists_chunk in _chunks(list(artists), 50):
        events = _get_bandsintown_events(artists_chunk, location)
        for event in events:
            all_events.append(event)
    return all_events

def spotify_auth():
    state = random_string()
    api_call = "https://accounts.spotify.com/authorize"
    args = [("client_id", config["SPOTIFY_ID"]),
            ("response_type", "code"),
            ("redirect_uri", "http://127.0.0.1:8000/spotify"),
            ("scope", "user-library-read"),
            ("state", state)]
    api_call = "%s?%s" % (api_call, urllib.urlencode(args))
    return api_call, state

def spotify_token(code):
    api_call = "https://accounts.spotify.com/api/token"
    response = requests.post(api_call, data={'code': code,
                                             'grant_type':'authorization_code',
                                             'redirect_uri':"http://127.0.0.1:8000/spotify",
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
                normalized_artist = _normalize_artist(artist["name"])
                all_artists.add(normalized_artist)
        iteration += 1
    return all_artists
