import datetime
import logging
import string
from dataclasses import dataclass

from app.data.database_driver import establish_connection


@dataclass
class User:
    user_key: string
    user_name: string
    last_enter: string

    def __init__(self, user_key, user_name, last_enter):
        self.user_key = user_key
        self.user_name = user_name
        self.last_enter = last_enter


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


def get_all_users():
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
                user = User(key, name, last_enter)
                users.append(user)

        connection.commit()

    return users
