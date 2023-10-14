import datetime
from dataclasses import dataclass

from app.data.database_driver import get_db_connection


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
    connection = get_db_connection()
    rows = connection.cursor().execute(
        "SELECT device_name, name, time FROM logs JOIN users u ON logs.key = u.key"
    ).fetchall()

    log_entries = []
    for row in rows:
        device_name, name, timestamp = row
        time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        log_entry = Log(device_name, name, time)
        log_entries.append(log_entry)

    connection.commit()

    return log_entries
