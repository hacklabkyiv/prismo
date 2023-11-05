import datetime


def convert_time_to_human(timestamp):
    if timestamp is None:
        return None
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
