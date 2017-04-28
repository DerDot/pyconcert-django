from datetime import date, datetime

import requests
from requests import HTTPError
from retrying import retry

from eventowl.utils import config

TOKEN = config['DISCOGS_TOKEN']

RECORDS_KEY = 'releases'
YEAR_KEY = 'year'
TYPE_KEY = 'type'
STATUS_KEY = 'status'
ID_KEY = 'id'
RELEASED_KEY = 'released'
RESULTS_KEY = 'results'
TITLE_KEY = 'title'
URL_KEY = 'uri'
USER_AGENT = 'EventOwl/0.1'

RELEASE_TYPE = 'release'
ACCEPTED_STATUS = 'Accepted'

YMD_LENGTH = 10


class Release:

    def __init__(self, title, relase_date, artists, url):
        self.title = title
        self.release_date = relase_date
        self.artists = artists
        self.url = url


@retry(wait_exponential_multiplier=500,
       wait_exponential_max=8000,
       stop_max_delay=50000)
def _call_api(url):
    response = requests.get(url, headers={'User-Agent': USER_AGENT, 'Accept-Encoding': 'gzip'})
    response.raise_for_status()
    return response


def artist_id_for_name(name):
    url = "https://api.discogs.com/database/search?q={name}&type=artist&token={token}".format(name=name, token=TOKEN)
    response = _call_api(url)
    artists = response.json()[RESULTS_KEY]
    if artists:
        return artists[0][ID_KEY]
    else:
        raise ValueError("No id for artist {}".format(name))


def records_for_artist_id(artist_id):
    url = "https://api.discogs.com/artists/{aid}/releases?sort=year&sort_order=desc".format(aid=artist_id)
    try:
        response = _call_api(url)
        records = response.json()[RECORDS_KEY]
        return [r for r in records if r[TYPE_KEY] == RELEASE_TYPE and r[STATUS_KEY] == ACCEPTED_STATUS]
    except (HTTPError, TimeoutError):
        return []


def record_details(record_id):
    url = "https://api.discogs.com/releases/{}".format(record_id)
    response = _call_api(url)
    return response.json()


def records_for_artist(name):
    records = []
    try:
        artist_id = artist_id_for_name(name)
        current_year = date.today().year

        for record in records_for_artist_id(artist_id):
            year = record.get(YEAR_KEY)
            if year is None or year < current_year:
                break
            detailed_record = record_details(record[ID_KEY])
            release_date = detailed_record[RELEASED_KEY]

            if len(release_date) != YMD_LENGTH:
                continue
            release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
            api_record = Release(
                detailed_record[TITLE_KEY],
                release_date,
                [name],
                detailed_record[URL_KEY]
            )
            records.append(api_record)
    except ValueError:
        pass

    return records


def records_for_artists(names):
    records = []
    for name in names:
        print("Getting records for {}...".format(name))
        records += records_for_artist(name)
    print("Got a total of {} records".format(len(records)))
    return records

records_for_artists(["kreator"])