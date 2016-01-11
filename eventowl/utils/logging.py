from eventowlproject.settings import LOG_LOCATIONS

def get_log(log_name, number_lines=100):
    path = LOG_LOCATIONS[log_name]
    with open(path) as log_file:
        lines = log_file.readlines()
    last_lines = lines[-number_lines:]
    return ''.join(last_lines)
