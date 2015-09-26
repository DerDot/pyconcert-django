from eventowl.utils.string_helpers import parse_json

with open("config.json") as config_file:
    config = parse_json(config_file.read())
