import time
import datetime
from dataclasses import dataclass

from app.data.database_driver import establish_connection
from app.data.time_convert import convert_time_to_human


@dataclass
class WorkLog:
    user_key: str
    user_name: str
    device_name: str
    start_time: str
    end_time: str

    def __init__(self, user_name, device_name, start_time, end_time):
        self.user_name = user_name
        self.device_name = device_name
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


def get_full_logs():
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "select u.name, d.name, start_time, end_time from work_logs join users u on u.key = work_logs.user_key join devices d on work_logs.device_id = d.id order by start_time desc")
            rows = cursor.fetchall()

            work_logs = []
            for row in rows:
                user_name, device_name, start_time, end_time = row
                human_start_time = convert_time_to_human(start_time)
                human_end_time = convert_time_to_human(end_time)
                work_log = WorkLog(user_name, device_name, human_start_time, human_end_time)
                work_logs.append(work_log)
        connection.commit()

    return work_logs
