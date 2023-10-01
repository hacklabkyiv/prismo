import time
from dataclasses import dataclass

from app.data.database_driver import establish_connection


@dataclass
class WorkLog:
    user_key: str
    device_id: str
    start_time: str
    end_time: str

    def __init__(self, user_key, device_id, start_time, end_time):
        self.user_key = user_key
        self.device_id = device_id
        self.start_time = start_time
        self.end_time = end_time


def start_work(user_key, device_id):
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO work_logs (user_key, device_id, start_time) values (%s, %s, %s)",
                           (user_key, device_id, time.time()))


def finish_work(user_key, device_id):
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE work_logs SET end_time = %s WHERE user_key = %s AND device_id = %s",
                           (time.time(), user_key, device_id))
