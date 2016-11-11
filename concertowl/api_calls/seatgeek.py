import random
import urllib

import requests

from eventowl.utils import config
from eventowl.utils.string_helpers import parse_json


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
    api_call = "%s?%s" % (api_call, urllib.parse.urlencode(args))
    resp = parse_json(requests.get(api_call).text)
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
    api_call = "%s?%s" % (api_call, urllib.parse.urlencode(args))
    resp = parse_json(requests.get(api_call).text)
    performers = resp['performers']
    if performers:
        return performers[0]['id']
    else:
        return None


def _random_subset(collection, size=20):
    if len(collection) > size:
        return random.sample(collection, size)
    return collection