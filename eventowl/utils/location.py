from ipware.ip import get_ip
from geoip2.database import Reader 
from geoip2.errors import AddressNotFoundError
from eventowl.utils.string_helpers import normalize

def current_position(request):
    ip = get_ip(request)
    reader = Reader('GeoLite2-City.mmdb')
    try:
        response = reader.city(ip)
        city = normalize(response.city.name)
        country = normalize(response.country.name)
    except (ValueError, AddressNotFoundError):
        city = country = None
        
    return city, country