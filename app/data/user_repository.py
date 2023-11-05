import logging
import string
from dataclasses import dataclass
from typing import List

from app.data.device_dto import DeviceDto
from app.data.dtos import UserDto
from app.features.admin.init_app import get_db_connection


@dataclass
class FullUser:
    user_key: string
    user_name: string
    logs: []
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


def get_user(user_key: str) -> UserDto | None:
    connection = get_db_connection()
    rows = connection.execute(
        "SELECT key, name FROM users WHERE key=?", (user_key,)
    ).fetchall()

    if len(rows) == 0:
        return None

    user_key, user_name = rows[0]
    user = UserDto(user_key, user_name)
    return user


def get_full_user(user_key):
    connection = get_db_connection()
    row = connection.execute(
        "SELECT key, name FROM users WHERE key=?", (user_key,)
    ).fetchall()

    if len(row) == 0:
        return None

    user_key, user_name = row[0]

    rows = connection.execute(
        "SELECT d.id, d.name FROM permissions JOIN devices d ON d.id = permissions.device_id "
        "WHERE permissions.user_key = ?", (user_key,)
    ).fetchall()

    user_devices = []
    for row in rows:
        device_id, device_name = row
        user_devices.append(UserDevices(device_name, device_id))

    rows = connection.execute(
        "select d.id, d.name, operation_type, operation_time from event_logs "
        "join devices d on d.id = event_logs.device_id "
        "WHERE event_logs.user_key=? "
        "ORDER BY operation_time DESC", (user_key,)
    ).fetchall()

    user_logs = []
    for row in rows:
        device_id, device_name, operation_type, operation_time = row
        device = DeviceDto(device_id, device_name)

        log = {
            "device": device,
            "operation_type": operation_type,
            "operation_time": operation_time
        }

        user_logs.append(log)

    full_user = FullUser(user_key, user_name, user_logs, user_devices)
    return full_user


def delete_user(user_key):
    connection = get_db_connection()
    connection.execute("DELETE FROM users WHERE key=?", (user_key,))
    connection.commit()
    logging.info('User with id %s was deleted' % (user_key,))


def add_user(user_name, user_key):
    connection = get_db_connection()
    connection.execute("INSERT INTO users(name, key) VALUES(?,?)", (user_name, user_key))
    logging.info('User added: %s, %s' % (user_name, user_key))
    connection.commit()


def get_all_users() -> list[UserDto]:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT key, name FROM users")
    rows = cursor.fetchall()

    users = []
    for row in rows:
        key, name = row
        user = UserDto(key, name)
        users.append(user)

    return users
