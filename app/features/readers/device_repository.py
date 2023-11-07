import logging
from dataclasses import dataclass
from typing import List

from app.data.device_dto import DeviceDto
from app.data.dtos import UserDto, OperationDto
from app.features.admin.init_app import get_db_connection


def get_all_devices() -> list[DeviceDto]:
    connection = get_db_connection()
    rows = connection.cursor().execute("SELECT id, name FROM devices order by name").fetchall()

    devices = []
    for row in rows:
        device_id, device_name = row
        device = DeviceDto(device_id, device_name)
        devices.append(device)

    return devices


def get_full_device(device_id):
    connection = get_db_connection()
    row = connection.cursor().execute("SELECT id, name, slack_channel_id FROM devices WHERE id=?",
                                      (device_id,)).fetchall()

    if len(row) == 0:
        return None

    device_id, device_name, slack_channel_id = row[0]

    rows = connection.cursor().execute(
        "SELECT u.key, u.name, operation_type, operation_time "
        "FROM event_logs "
        "join users u on u.key = user_key "
        "WHERE device_id=? order by operation_time desc", (device_id,)
    ).fetchall()

    logs = []
    for row in rows:
        user_key, user_name, operation_type, operation_time = row
        user = UserDto(user_key, user_name)
        operation = OperationDto(operation_time, operation_type)

        logs.append({
            "user": user,
            "operation": operation,
        })

    rows = connection.cursor().execute(
        "SELECT u.key, u.name FROM permissions JOIN users u ON u.key = permissions.user_key WHERE "
        "permissions.device_id=?", (device_id,)
    ).fetchall()
    user_with_access = []
    for row in rows:
        user_key, user_name = row
        user_with_access.append(UserDto(user_key, user_name))

    return {
        "device": {
            "name": device_name,
            "id": device_id,
            "slack_channel_id": slack_channel_id,
        },
        "logs": logs,
        "user_with_access": user_with_access,
    }


def add_device(device_id, device_name):
    connection = get_db_connection()
    connection.execute("INSERT INTO devices(id, name) VALUES(?,?)", (device_id, device_name))
    logging.info('Device added: %s, %s', (device_id, device_name))
    connection.commit()
