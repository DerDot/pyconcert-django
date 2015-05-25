from amazon.api import AmazonAPI
import json
from datetime import date

with open('amazon.config') as configfile:
    config = json.load(configfile)

amazon = AmazonAPI(str(config['AWS_ACCESS_KEY_ID']),
                   str(config['AWS_SECRET_ACCESS_KEY']),
                   str(config['AWS_ASSOCIATE_TAG']),
                   region='US')

results = amazon.search(Author='ben aaronovitch',
                        Sort='-publication_date',
                        SearchIndex='Books')

for item in results:
    if item.publication_date >= date.today():
        if item.edition != "Reprint" and item.binding == "Hardcover":
            print item.title
            print item.publication_date
            print item.offer_url
            print item.authors
            print item.isbn
    else:
        break