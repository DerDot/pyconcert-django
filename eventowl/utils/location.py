from ipware.ip import get_ip
from geoip2.database import Reader 
from geoip2.errors import AddressNotFoundError

def current_position(request):
    ip = get_ip(request)
    reader = Reader('GeoLite2-City.mmdb')
    try:
        response = reader.city(ip)
        city = response.city.name
        country = response.country.name
    except (ValueError, AddressNotFoundError):
        city = country = None
        
    return city, country