import string
import random

try:
    import cjson
    parse_json = cjson.decode
except ImportError:
    import json
    parse_json = json.loads

def normalize(name):
    if isinstance(name, unicode):
        name = name.encode("utf8")
    return name.lower()


def random_string(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))