import datetime
import logging
import string
from dataclasses import dataclass
from typing import List

from app.data.database_driver import establish_connection
from app.data.time_convert import convert_time_to_human
from app.data.user_dto import UserDto


@dataclass
class UserWithLastEnter:
    user: UserDto
    last_enter: string

    def __init__(self, user, last_enter):
        self.user = user
        self.last_enter = last_enter


@dataclass
class UserWorkLog:
    device_name: str
    start_time: str
    end_time: str

    def __init__(self, device_name, start_time, end_time):
        self.device_name = device_name
        self.start_time = start_time
        self.end_time = end_time


@dataclass
class FullUser:
    user_key: string
    user_name: string
    logs: List[UserWorkLog]
    devices: List[str]

    def __init__(self, user_key, user_name, logs, devices):
        self.user_key = user_key
        self.user_name = user_name
        self.logs = logs
        self.devices = devices


class UserDevices:
    device_name: str
    device_id: str

    def __init__(self, device_name, device_id):
        self.device_name = device_name
        self.device_id = device_id


def get_user(user_key: str) -> UserDto:
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT key, name FROM users WHERE key=%s", (user_key,))
            row = cursor.fetchall()

            if len(row) == 0:
                return None

            user_key, user_name = row[0]
            user = UserDto(user_key, user_name)
        connection.commit()
    return user


def get_full_user(user_key):
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT key, name FROM users WHERE key=%s", (user_key,))
            row = cursor.fetchall()

            if len(row) == 0:
                return None

            user_key, user_name = row[0]

            cursor.execute(
                "SELECT d.id, d.name FROM permissions JOIN devices d ON d.id = permissions.device_id WHERE permissions.user_key = %s",
                (user_key,))
            rows = cursor.fetchall()
            user_devices = []
            for row in rows:
                device_id, device_name = row
                user_devices.append(UserDevices(device_name, device_id))

            cursor.execute(
                "SELECT d.name, start_time, end_time FROM work_logs JOIN devices d ON work_logs.device_id = d.id WHERE work_logs.user_key=%s ORDER BY start_time DESC",
                (user_key,))
            rows = cursor.fetchall()
            user_logs = []
            for row in rows:
                device, start_time, end_time = row
                human_start_time = convert_time_to_human(start_time)
                human_end_time = convert_time_to_human(end_time)
                user_logs.append(UserWorkLog(device, human_start_time, human_end_time))

            full_user = FullUser(user_key, user_name, user_logs, user_devices)
        connection.commit()
    return full_user


def delete_user(user_key):
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM users WHERE key=%s', (user_key,))
        logging.info('User with id %s was deleted' % (user_key,))
        connection.commit()


def add_user(user_name, user_key):
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO users(name, key) VALUES(%s, %s)', (user_name, user_key))
        logging.info('User added: %s, %s' % (user_name, user_key))
        connection.commit()


def get_all_users() -> list[UserWithLastEnter]:
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT key, name, last_enter FROM users")
            rows = cursor.fetchall()

            users = []
            for row in rows:
                key, name, last_enter_timestamp = row
                if last_enter_timestamp is None:
                    last_enter = None
                else:
                    last_enter = datetime.datetime.fromtimestamp(last_enter_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                user = UserWithLastEnter(UserDto(key, name), last_enter)
                users.append(user)

        connection.commit()

    return users
