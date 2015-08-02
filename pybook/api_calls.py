from eventowl.common_utils import config, normalize

import bottlenose
from datetime import date
from itertools import izip

import xmltodict

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

def _parse_date(date_string, format="%Y-%m-%d"):
    try:
        date.strftime(date_string, format)
    except:
        return None


def _book_release(author, api):
    search_result = api.ItemSearch(Author=author,
                                  Sort='-publication_date',
                                  SearchIndex='Books',
                                  ResponseGroup='ItemAttributes')
    search_result_parsed = xmltodict.parse(search_result)
    items_dict = search_result_parsed['ItemSearchResponse']['Items']
    num_results = int(items_dict['TotalResults'])

    if num_results == 0:
        return []

    api_releases = items_dict['Item']
    if num_results == 1:
        api_releases = [api_releases]

    num_releases = 0
    releases = []
    for api_release in api_releases:
        attributes = api_release['ItemAttributes']
        publication_date = _parse_date(attributes.get('PublicationDate'))
        if (publication_date is not None and
            publication_date >= date.today() and
            num_releases < 5):
            if attributes.edition != "Reprint" and attributes['Binding'] == "Hardcover":
                release = Release(attributes['Title'],
                                  attributes['ISBN'],
                                  publication_date,
                                  attributes['OfferUrl'],
                                  [normalize(attributes['Author'])]) #TODO: other authors?
                releases.append(release)
                num_releases += 1
        else:
            break

    return releases

def book_releases(authors, region):
    api = bottlenose.Amazon(str(config['AWS_ACCESS_KEY_ID']),
                            str(config['AWS_SECRET_ACCESS_KEY']),
                            str(config['AWS_ASSOCIATE_TAG']),
                            MaxQPS=0.9)

    releases = []
    for idx, author in enumerate(authors):
        print u"Working on author number {} of {} ({})".format(idx + 1, len(authors), author)
        author_releases = _book_release(author, api)
        releases += author_releases

    return releases
