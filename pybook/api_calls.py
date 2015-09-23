from datetime import date
from itertools import izip
import urllib

import xmltodict

from eventowl.common_utils import config, normalize
from eventowl.utils import as_list

GOODREADS_URL = 'https://goodreads.com'


class Release(object):

    def __init__(self, title, isbn, date, url, authors):
        self.title = title
        self.isbn = isbn
        self.date = date
        self.buy_url = url
        self.authors = authors

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
    url = '{base_url}/author/list/{author_id}?key={key}&page={page}'.format(**url_parameters)
    resp = urllib.urlopen(url).read()
    print "    Got response"
    parsed = xmltodict.parse(resp)
    print "    Parsed response"
    results = parsed['GoodreadsResponse']['author']['books']['book']
    num_books_current = parsed['GoodreadsResponse']['author']['books']['@end']
    num_books_total = parsed['GoodreadsResponse']['author']['books']['@total']
    return results, num_books_current < num_books_total


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


def _book_release(author_name):
    author_id = _id_for_author_name(author_name)
    author_books = _books_by_author(author_id)

    releases = []
    for book in author_books:
        publication_date = _publication_date(book)
        if (publication_date is not None and
            publication_date >= date.today()):
            authors = as_list(book['authors']['author'])
            normalized_authors = [normalize(author['name']) for author in authors]
            release = Release(book['title'],
                              book['isbn'],
                              publication_date,
                              book['link'],
                              normalized_authors)
            releases.append(release)

    return releases


def book_releases(authors):
    releases = []
    for idx, author in enumerate(authors):
        print u"Working on author number {} of {} ({})".format(idx + 1, len(authors), author)
        author_releases = _book_release(author)
        releases += author_releases

    return releases