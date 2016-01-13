import string
import random

try:
    import cjson
    parse_json = cjson.decode
except ImportError:
    import json
    parse_json = json.loads

def normalize(name):
    return name.lower().strip()


def random_string(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def as_filename(s):
    return s.lower().replace(' ', '_')