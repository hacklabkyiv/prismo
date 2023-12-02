import logging

from app.data.device_dto import DeviceDto
from app.data.dtos import UserDto, OperationDto
from app.features.admin.init_app import get_db_connection


def get_full_user(user_key):
    connection = get_db_connection()
    row = connection.execute(
        "SELECT key, name, slack_id FROM users WHERE key=?", (user_key,)
    ).fetchall()

    if len(row) == 0:
        return None

    user_key, user_name, slack_id = row[0]

    rows = connection.execute(
        "SELECT d.id, d.name FROM permissions JOIN devices d ON d.id = permissions.device_id "
        "WHERE permissions.user_key = ?", (user_key,)
    ).fetchall()

    user_devices = []
    for row in rows:
        device_id, device_name = row
        user_devices.append(DeviceDto(device_name, device_id))

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
            "operation": OperationDto(operation_time, operation_type),
        }

        user_logs.append(log)

    return {
        "user": {
            "key": user_key,
            "name": user_name,
            "slack_id": slack_id
        },
        "logs": user_logs,
        "devices": user_devices
    }


def delete_user(user_key):
    connection = get_db_connection()
    connection.execute("DELETE FROM users WHERE key=?", (user_key,))
    connection.commit()
    logging.info('User with id %s was deleted', user_key)


def add_user(user_name, user_key):
    connection = get_db_connection()
    connection.execute("INSERT INTO users(name, key) VALUES(?,?)", (user_name, user_key))
    logging.info('User added: %s, %s', user_name, user_key)
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
