import logging
from dataclasses import dataclass
from typing import List

from app.data.database_driver import establish_connection


@dataclass
class UserPermission:
    user_key: str
    permissions: List[str]

    def __init__(self, user_key, permissions):
        self.user_key = user_key
        self.permissions = permissions


def get_user_permissions(user_key) -> List[str]:
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT device_id FROM permissions WHERE user_key = %s", (user_key,))
            rows = cursor.fetchall()

            user_permissions = []
            for row in rows:
                key, = row
                user_permissions.append(key)

    connection.commit()

    logging.info('user with id %s, permissions: %s' % (user_key, user_permissions))

    return user_permissions

def get_user_with_permission_to_device(device_id):
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_key FROM permissions WHERE device_id = %s", (device_id,))
            rows = cursor.fetchall()

            users = []
            for row in rows:
                key, = row
                users.append(key)

    return users

def grant_permission(user_key, device_id):
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO permissions(user_key, device_id) VALUES (%s, %s)', (user_key, device_id))
        logging.info('Grant permission for user with id %s to device %s' % (user_key, device_id))
        connection.commit()


def reject_permission(user_key, device_id):
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('delete from permissions where user_key=%s and device_id=%s', (user_key, device_id))
        logging.info('Reject permission for user with id %s to device %s' % (user_key, device_id))
        connection.commit()
