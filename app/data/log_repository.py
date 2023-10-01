import datetime
import logging
import os
import sys
from dataclasses import dataclass

import yaml

from app.data.database_driver import establish_connection

try:
    from yaml import CLoader as Loader, CDumper
except ImportError:
    from yaml import Loader

# Configuration file
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../config.cfg')

try:
    cfg = yaml.load(open(CONFIG_FILE, 'r'), Loader=Loader)
except IOError as e:
    logging.error("Config file not found!")
    logging.error("Exception: %s" % str(e))
    sys.exit(1)


@dataclass
class Log:
    device_name: str
    user_name: str
    time: str

    def __init__(self, device_name, user_name, time):
        self.device_name = device_name
        self.user_name = user_name
        self.time = time


def get_logs():
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT device_name, name, time FROM logs JOIN users u ON logs.key = u.key")
            rows = cursor.fetchall()

            log_entries = []
            for row in rows:
                device_name, name, timestamp = row
                time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                log_entry = Log(device_name, name, time)
                log_entries.append(log_entry)

        connection.commit()

    return log_entries
