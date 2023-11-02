import hashlib

import flask_login

from app.config import cfg
from app.data.database import get_db_connection

salt = cfg['app']['slat']


class FlaskAdminUser(flask_login.UserMixin):
    pass


class AdminUser:
    id: int
    username: str
    password: str

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def get_flask_admin_user_by_credentials(username: str, password: str) -> FlaskAdminUser | None:
    connection = get_db_connection()
    rows = connection.execute(
        "SELECT id, password FROM admins WHERE username=?", (username,)
    ).fetchall()

    if len(rows) == 0:
        return None

    final_slat = salt + str(len(password))
    hashed_pass = hashlib.sha256((password + final_slat).encode('utf-8')).hexdigest()

    db_admin_id, db_password = rows[0]
    if db_password == hashed_pass:
        user = FlaskAdminUser()
        user.id = db_admin_id
        connection.close()
        return user
    else:
        return None


def get_flask_admin_user_by_id(user_id: str) -> FlaskAdminUser | None:
    user = get_admin_user_by_id(user_id)
    if user is None:
        return None
    else:
        flask_user = FlaskAdminUser()
        flask_user.id = user.id
        return flask_user


def get_flask_admin_user_by_user_name(user_name: str) -> FlaskAdminUser | None:
    user = get_admin_user_by_user_name(user_name)
    if user is None:
        return None
    else:
        flask_user = FlaskAdminUser()
        flask_user.id = user.id
        return flask_user


def get_admin_user_by_flask_user(flask_user) -> AdminUser | None:
    if flask_user.is_anonymous:
        return None
    return get_admin_user_by_id(flask_user.id)


def get_admin_user_by_id(user_id: str) -> AdminUser | None:
    connection = get_db_connection()
    rows = connection.execute(
        "SELECT id, username, password FROM admins WHERE id=?", (user_id,)
    ).fetchall()

    if len(rows) == 0:
        return None

    admin_id, username, password = rows[0]
    user = AdminUser(admin_id, username, password)
    connection.close()
    return user


def get_admin_user_by_user_name(user_name: str) -> AdminUser | None:
    connection = get_db_connection()
    rows = connection.execute(
        "SELECT id, username, password FROM admins WHERE username=?", (user_name,)
    ).fetchall()

    if len(rows) == 0:
        return None

    admin_id, username, password = rows[0]
    user = AdminUser(admin_id, username, password)
    connection.close()
    return user


def is_any_admin_user_exists() -> bool:
    connection = get_db_connection()
    rows = connection.execute(
        "SELECT id FROM admins"
    ).fetchall()

    return len(rows) > 0
