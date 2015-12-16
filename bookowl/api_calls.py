from collections import OrderedDict
from datetime import date
from itertools import izip
import urllib

import bottlenose
import xmltodict

from eventowl.utils import config
from eventowl.utils.string_helpers import normalize
from eventowl.utils.collection_helpers import as_list

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
        for self_var, other_var in izip(vars(self), vars(other)):
            if self_var != other_var:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


def _publication_date(book):
    day = book['publication_day']
    month = book['publication_month']
    year = book['publication_year']
    if day is None or month is None or year is None:
        return None
    else:
        return date(int(year),
                    int(month),
                    int(day))


def _id_for_author_name(author_name):
    print "    Getting ID..."
    url_parameters = {'base_url': GOODREADS_URL,
                      'author_name': author_name,
                      'key': config['GOODREADS_KEY']}

    url = '{base_url}/api/author_url/{author_name}?key={key}'.format(**url_parameters)
    resp = urllib.urlopen(url).read()
    print "    Got response"
    result = xmltodict.parse(resp)
    print "    Parsed Response"
    return result['GoodreadsResponse']['author']['@id']


def _call_book_api(url_parameters):
    print "    Reading page", url_parameters['page']
    url = u'{base_url}/author/list/{author_id}?key={key}&page={page}'.format(**url_parameters)
    url = url.encode('utf8')
    resp = urllib.urlopen(url).read()
    print "    Got response"
    parsed = xmltodict.parse(resp)
    results = parsed['GoodreadsResponse']['author']['books']['book']
    num_books_current = parsed['GoodreadsResponse']['author']['books']['@end']
    num_books_total = parsed['GoodreadsResponse']['author']['books']['@total']
    print "    Parsed {} of {} books".format(num_books_current, num_books_total)
    return results, num_books_current < num_books_total


def _call_title_api(url_parameters):
    url = u'{base_url}/book/title/{title}?key={key}&author={author}'.format(**url_parameters)
    url = url.encode('utf8')
    resp = urllib.urlopen(url).read()
    parsed = xmltodict.parse(resp)
    api_book = parsed['GoodreadsResponse']['book']
    return _release_from_api_book(api_book)


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
    release = Release(book['title'],
                      isbn,
                      _publication_date(book),
                      book['link'],
                      normalized_authors,
                      book['image_url'])
    return release


def _book_release(author_name):
    author_id = _id_for_author_name(author_name)
    author_books = _books_by_author(author_id)

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
        print u"Working on author number {} of {} ({})".format(idx + 1, len(authors), author)
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
    previews = []
    print "Getting new releases..."
    new_releases = _new_releases()
    for author_name, title in new_releases:
        print "Getting info for {} by {}...".format(normalize(title), normalize(author_name))
        preview = _book_by_title_and_author(author_name, title)
        if 'nophoto' in preview.image:
            print "No photo. Skip..."
            continue
        print "Done"
        previews.append(preview)
    return previews
