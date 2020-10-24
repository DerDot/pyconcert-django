from eventowl.utils.string_helpers import normalize
from geoip2.errors import AddressNotFoundError
from geoip2.database import Reader
from ipware import get_client_ip
import logging
logger = logging.getLogger(__name__)


READER = Reader('vendor/maxmind.mmdb')


def current_position(request):
    ip, _ = get_client_ip(request)
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
