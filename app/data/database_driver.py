import sqlite3

import psycopg2 as psycopg

from app.config import cfg


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def establish_connection():
    return psycopg.connect(
        user=cfg['data']['user'],
        password=cfg['data']['password'],
        host=cfg['data']['host'],
        port=cfg['data']['port'],
        database=cfg['data']['name']
    )
