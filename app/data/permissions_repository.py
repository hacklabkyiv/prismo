import logging
from dataclasses import dataclass
from typing import List

from app.data.database_driver import get_db_connection


@dataclass
class UserPermission:
    user_key: str
    permissions: List[str]

    def __init__(self, user_key, permissions):
        self.user_key = user_key
        self.permissions = permissions


def get_user_permissions(user_key) -> List[str]:
    connection = get_db_connection()
    rows = connection.cursor().execute(
        "SELECT device_id FROM permissions WHERE user_key = ?", (user_key,)
    ).fetchall()

    user_permissions = []
    for row in rows:
        key, = row
        user_permissions.append(key)

    connection.close()

    logging.info('user with id %s, permissions: %s' % (user_key, user_permissions))
    return user_permissions


def get_user_with_permission_to_device(device_id):
    connection = get_db_connection()
    rows = connection.cursor().execute(
        "SELECT user_key FROM permissions WHERE device_id = ?", (device_id,)
    ).fetchall()
    users = []
    for row in rows:
        key, = row
        users.append(key)

    return users


def grant_permission(user_key, device_id):
    connection = get_db_connection()
    connection.cursor().execute(
        "INSERT INTO permissions(user_key, device_id) VALUES (?, ?)", (user_key, device_id)
    )
    logging.info('Grant permission for user with id %s to device %s' % (user_key, device_id))
    connection.commit()


def reject_permission(user_key, device_id):
    connection = get_db_connection()
    connection.cursor().execute(
        "delete from permissions where user_key=? and device_id=?", (user_key, device_id)
    )
    connection.commit()
    connection.close()
    logging.info('Reject permission for user with id %s to device %s' % (user_key, device_id))
