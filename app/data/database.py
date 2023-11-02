import hashlib
import os
import sqlite3
from pathlib import Path

from werkzeug.utils import secure_filename

from app.config import cfg

database_path = Path("database.db")

password_slat = cfg['app']['slat']

_database_connection = None


def is_app_inited():
    return database_path.is_file()


def hash_password(password: str):
    final_slat = password_slat + str(len(password))
    hashed_pass = hashlib.sha256((password + final_slat).encode('utf-8')).hexdigest()
    return hashed_pass


def init_app_database(admin_username: str, admin_password: str, file):
    if is_app_inited():
        raise Exception("Database already exists")
    if (file is not None) and (not file.filename == ''):
        init_database_from_backup(admin_username, admin_password, file)
    else:
        init_database(admin_username, admin_password)


def init_database_from_backup(admin_username: str, admin_password: str, file):
    if file.filename == '':
        raise Exception("Invalid file name")

    filename = secure_filename(file.filename)
    if not filename.endswith(".db"):
        raise Exception("Invalid file extension")
    file.save(database_path)

    verify_is_secrets_from_backup(admin_password, admin_username)


def verify_is_secrets_from_backup(admin_password, admin_username):
    cursor = get_db_connection().cursor()
    rows = cursor.execute(
        "SELECT * FROM admins where username = ? and password= ?",
        (admin_username, hash_password(admin_password))
    ).fetchone()
    if (rows is None) or (len(rows) == 0):
        os.remove(database_path)
        raise Exception("Invalid admin credentials")


def init_database(admin_username: str, admin_password: str):
    sqlite3.connect(database_path)
    connection = get_db_connection()
    connection.executescript("""
    CREATE TABLE admins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    );
    
    CREATE TABLE users(
        name TEXT NOT NULL,
        key  TEXT NOT NULL
    );
    
    CREATE TABLE devices(
        id   TEXT NOT NULL,
        name TEXT NOT NULL
    );
    
    CREATE TABLE permissions(
        device_id TEXT NOT NULL,
        user_key  TEXT NOT NULL
    );
    
    CREATE TABLE work_logs(
        user_key   TEXT NOT NULL,
        device_id  TEXT NOT NULL,
        start_time INTEGER,
        end_time   INTEGER
    );
    """)
    connection.commit()

    connection = get_db_connection()
    connection.execute(
        "INSERT INTO admins(username, password) VALUES (?, ?)",
        (admin_username, hash_password(admin_password))
    )
    connection.commit()


def get_db_connection():
    if not is_app_inited():
        return None
    _database_connection = sqlite3.connect(database_path)
    _database_connection.row_factory = sqlite3.Row
    return _database_connection
