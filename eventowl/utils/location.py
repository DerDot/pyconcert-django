import logging
logger = logging.getLogger(__name__)

from ipware.ip import get_ip
from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError
from eventowl.utils.string_helpers import normalize

READER = Reader('vendor/maxmind.mmdb')

def current_position(request):
    ip = get_ip(request)
    try:
        response = READER.city(ip)
        city = response.city.name
        if city is not None:
            city = normalize(city)

        country = response.country.name
        if country is not None:
            country = normalize(country)
    except (ValueError, AddressNotFoundError, AttributeError) as e:
        logger.warn(str(e))
        city = country = None

    return city, country
