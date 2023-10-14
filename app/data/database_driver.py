import psycopg2 as psycopg

from app.config import cfg


def establish_connection():
    return psycopg.connect(
        user=cfg['data']['user'],
        password=cfg['data']['password'],
        host=cfg['data']['host'],
        port=cfg['data']['port'],
        database=cfg['data']['name']
    )
