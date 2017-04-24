from collections import OrderedDict
from datetime import date

import logging
import requests

import bottlenose
import xmltodict

from eventowl.utils import config
from eventowl.utils.string_helpers import normalize
from eventowl.utils.collection_helpers import as_list

logger = logging.getLogger(__name__)

GOODREADS_URL = 'https://goodreads.com'


class Release(object):

    def __init__(self, title, isbn, date, url, authors, image=None):
        self.title = title
        self.isbn = isbn
        self.date = date
        self.buy_url = url
        self.authors = authors
        self.image = image

    def __str__(self):
        return "{title} ({isbn}) by {authors} released on {date}.".format(title=self.title,
                                                                          isbn=self.isbn,
                                                                          authors=", ".join(self.authors),
                                                                          date=self.date)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        for self_var, other_var in zip(vars(self), vars(other)):
            if self_var != other_var:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


def _publication_date(book):
    day = book.get('publication_day')
    month = book.get('publication_month')
    year = book.get('publication_year')
    if day is None or month is None or year is None:
        return None
    else:
        year = int(year)
        month = int(month)
        day = int(day)
        return _try_dates(year, month, day)


def _try_dates(year, month, day):
    try:
        return date(year, month, day)
    except ValueError:
        try:
            return date(year, month, "1")
        except ValueError:
            return None


def _id_for_author_name(author_name):
    print("    Getting ID...")
    url_parameters = {'base_url': GOODREADS_URL,
                      'author_name': author_name,
                      'key': config['GOODREADS_KEY']}

    url = '{base_url}/api/author_url/{author_name}?key={key}'.format(**url_parameters)
    resp = requests.get(url)
    print("    Got response")
    result = xmltodict.parse(resp.text)
    print("    Parsed Response")
    response = result['GoodreadsResponse']
    return response['author']['@id'] if 'author' in response else None


def _call_book_api(url_parameters):
    print("    Reading page {}".format(url_parameters['page']))
    url = '{base_url}/author/list/{author_id}?key={key}&page={page}'.format(**url_parameters)
    resp = requests.get(url)
    print("    Got response")
    parsed = xmltodict.parse(resp.text)
    results = parsed['GoodreadsResponse']['author']['books']['book']
    if not isinstance(results, list):
        results = [results]
    num_books_current = parsed['GoodreadsResponse']['author']['books']['@end']
    num_books_total = parsed['GoodreadsResponse']['author']['books']['@total']
    print(("    Parsed {} of {} books".format(num_books_current, num_books_total)))
    return results, num_books_current < num_books_total


def _call_title_api(url_parameters):
    url = '{base_url}/book/title.xml/?title={title}&key={key}&author={author}'.format(**url_parameters)
    resp = requests.get(url)
    try:
        parsed = xmltodict.parse(resp.text)
    except:
        return None
    try:
        api_book = parsed['GoodreadsResponse']['book']
        return _release_from_api_book(api_book)
    except KeyError:
        return None


def _books_by_author(author_id):
    url_parameters = {'base_url': GOODREADS_URL,
                      'author_id': author_id,
                      'key': config['GOODREADS_KEY'],
                      'page': 1}

    all_results, more_pages = _call_book_api(url_parameters)
    while more_pages:
        url_parameters['page'] += 1
        results, more_pages = _call_book_api(url_parameters)
        all_results.extend(results)

    return all_results


def _book_by_title_and_author(author_name, title):
    url_parameters = {'base_url': GOODREADS_URL,
                      'author': author_name,
                      'title': title,
                      'key': config['GOODREADS_KEY']}
    return _call_title_api(url_parameters)


def _release_from_api_book(book):
    authors = as_list(book['authors']['author'])
    normalized_authors = [normalize(author['name']) for author in authors]
    api_isbn = book['isbn']
    isbn = None if isinstance(api_isbn, OrderedDict) else api_isbn
    release = Release(normalize(book['title']),
                      isbn,
                      _publication_date(book),
                      book['link'],
                      normalized_authors,
                      book['image_url'])
    return release


def _book_release(author_name):
    author_id = _id_for_author_name(author_name)
    if author_id is None:
        return []
    try:
        author_books = _books_by_author(author_id)
    except Exception as e:
        logger.error("Couldn't get book releases for {}: {}".format(author_name, e))
        return []

    releases = []
    for book in author_books:
        publication_date = _publication_date(book)
        if (publication_date is not None and
            publication_date >= date.today()):
            release = _release_from_api_book(book)
            releases.append(release)

    return releases


def book_releases(authors):
    releases = []
    for idx, author in enumerate(authors):
        print(("Working on author number {} of {} ({})".format(idx + 1, len(authors), author)))
        author_releases = _book_release(author)
        releases += author_releases

    return releases


def _new_releases():
    api = bottlenose.Amazon(str(config['AWS_ACCESS_KEY_ID']),
                            str(config['AWS_SECRET_ACCESS_KEY']),
                            str(config['AWS_ASSOCIATE_TAG']),
                            MaxQPS=0.9)
    lookup_result = api.BrowseNodeLookup(BrowseNodeId=283155,
                                         ResponseGroup='NewReleases')
    new_releases = xmltodict.parse(lookup_result)
    actual_releases = new_releases['BrowseNodeLookupResponse']['BrowseNodes']['BrowseNode']['NewReleases']['NewRelease']
    for release in actual_releases:
        asin = release['ASIN']
        lookup_result = api.ItemLookup(ItemId=asin)
        item = xmltodict.parse(lookup_result)
        author = item['ItemLookupResponse']['Items']['Item']['ItemAttributes']['Author']
        if isinstance(author, list):
            author = author[0]
        title = item['ItemLookupResponse']['Items']['Item']['ItemAttributes']['Title']
        yield author, title


def previews():
    api_previews = []
    print("Getting new releases...")
    new_releases = _new_releases()
    for author_name, title in new_releases:
        print(("Getting info for {} by {}...".format(normalize(title), normalize(author_name))))
        preview = _book_by_title_and_author(author_name, title)
        if preview is None:
            print("Couldn't get information. Skip...")
            continue
        if 'nophoto' in preview.image:
            print("No photo. Skip...")
            continue
        print("Done")
        api_previews.append(preview)
    return api_previews