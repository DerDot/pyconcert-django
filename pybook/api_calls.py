from eventowl.common_utils import config, normalize

from amazon.api import AmazonAPI
from datetime import date
from itertools import izip
from time import sleep

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

def _book_release(author, api):
    api_releases = api.search(Author=author,
                              Sort='-publication_date',
                              SearchIndex='Books')

    num_releases = 0
    releases = []
    for api_release in api_releases:
        print num_releases
        sleep(1.1)
        if (api_release.publication_date is not None and
            api_release.publication_date >= date.today() and
            num_releases < 5):
            if api_release.edition != "Reprint" and api_release.binding == "Hardcover":
                release = Release(api_release.title,
                                  api_release.isbn,
                                  api_release.publication_date,
                                  api_release.offer_url,
                                  [normalize(author) for author in api_release.authors])
                releases.append(release)
                num_releases += 1
        else:
            break

    return releases

def book_releases(authors, region):
    api = AmazonAPI(str(config['AWS_ACCESS_KEY_ID']),
                       str(config['AWS_SECRET_ACCESS_KEY']),
                       str(config['AWS_ASSOCIATE_TAG']),
                       region=region)

    releases = []
    for idx, author in enumerate(authors):
        print "Working on author number {} of {} ({})".format(idx + 1, len(authors), author)
        author_releases = _book_release(author, api)
        releases += author_releases
        sleep(1)

    return releases
