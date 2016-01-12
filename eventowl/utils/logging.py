def get_log(log_path, number_lines=100):
    with open(log_path) as log_file:
        lines = log_file.readlines()
    last_lines = lines[-number_lines:]
    return ''.join(last_lines)
