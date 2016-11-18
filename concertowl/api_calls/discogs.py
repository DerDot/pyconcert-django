from datetime import date, datetime

import discogs_client
import requests
from retrying import retry

from eventowl.utils import config

TOKEN = config['DISCOGS_TOKEN']
USER_AGENT = 'EventOwl/0.1'
CLIENT = discogs_client.Client(USER_AGENT, user_token=TOKEN)

SEARCH_TYPE = 'release'

RELEASED_KEY = 'released'
TITLE_KEY = 'title'
URL_KEY = 'uri'


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


def record_details(record_id):
    url = "https://api.discogs.com/releases/{}".format(record_id)
    response = _call_api(url)
    return response.json()


def records_for_artist(name):
    records = []
    current_year = date.today().year

    search_result = CLIENT.search(type=SEARCH_TYPE, artist=name)
    for release in search_result:
        year = int(release.year)
        if year < current_year - 1:
            break
        detailed_record = record_details(release.id)
        release_date = detailed_record.get(RELEASED_KEY, '')
        try:
            release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
        except ValueError:
            continue
        api_record = Release(
            detailed_record[TITLE_KEY],
            release_date,
            [name],
            detailed_record[URL_KEY]
        )
        records.append(api_record)

    return records


def records_for_artists(names):
    records = []
    for name in names:
        print("Getting records for {}...".format(name))
        records += records_for_artist(name)
    print("Got a total of {} records".format(len(records)))
    return records