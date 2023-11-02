import logging
from dataclasses import dataclass
from typing import List

from app.init_app import get_db_connection
from app.data.device_dto import DeviceDto
from app.data.time_convert import convert_time_to_human
from app.data.user_dto import UserDto


def get_all_devices() -> list[DeviceDto]:
    connection = get_db_connection()
    rows = connection.cursor().execute("SELECT id, name FROM devices order by name").fetchall()

    devices = []
    for row in rows:
        device_id, device_name = row
        device = DeviceDto(device_id, device_name)
        devices.append(device)

    connection.close()
    return devices


@dataclass
class DeviceLog:
    user: UserDto
    start_time: str
    end_time: str

    def __init__(self, user, start_time, end_time):
        self.user = user
        self.start_time = start_time
        self.end_time = end_time


@dataclass
class FullDevice:
    device_id: str
    device_name: str
    user_with_access: List[UserDto]
    logs: List[DeviceLog]

    def __init__(self, device_id, device_name, logs, user_with_access):
        self.device_id = device_id
        self.device_name = device_name
        self.logs = logs
        self.user_with_access = user_with_access


def get_full_device(device_id) -> FullDevice:
    connection = get_db_connection()
    row = connection.cursor().execute("SELECT id, name FROM devices WHERE id=?", (device_id,)).fetchall()

    if len(row) == 0:
        return None

    device_id, device_name = row[0]

    rows = connection.cursor().execute(
        "SELECT u.key, u.name, start_time, end_time FROM work_logs join users u on u.key = user_key "
        "WHERE device_id=? order by start_time desc", (device_id,)
    ).fetchall()

    logs = []
    for row in rows:
        user_key, user_name, start_time, end_time = row
        human_start_time = convert_time_to_human(start_time)
        human_end_time = convert_time_to_human(end_time)
        logs.append(DeviceLog(UserDto(user_key, user_name), human_start_time, human_end_time))

    rows = connection.cursor().execute(
        "SELECT u.key, u.name FROM permissions JOIN users u ON u.key = permissions.user_key WHERE "
        "permissions.device_id=?", (device_id,)
    ).fetchall()
    user_with_access = []
    for row in rows:
        user_key, user_name = row
        user_with_access.append(UserDto(user_key, user_name))

    connection.close()

    full_device = FullDevice(device_id, device_name, logs, user_with_access)

    logging.info("full device: %s" % full_device)

    return full_device

def add_device(device_id, device_name):
    connection = get_db_connection()
    connection.execute("INSERT INTO devices(id, name) VALUES(?,?)", (device_id, device_name))
    logging.info('Device added: %s, %s' % (device_id, device_name))
    connection.commit()
    connection.close()