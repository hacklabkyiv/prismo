import logging
import os
import sys
import yaml

import psycopg2 as psycopg

try:
    from yaml import CLoader as Loader, CDumper
except ImportError:
    from yaml import Loader

# Configuration file
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../config.cfg')

try:
    cfg = yaml.load(open(CONFIG_FILE, 'r'), Loader=Loader)
except IOError as e:
    logging.error("Config file not found!")
    logging.error("Exception: %s" % str(e))
    sys.exit(1)


def establish_connection():
    return psycopg.connect(
        user=cfg['data']['user'],
        password=cfg['data']['password'],
        host=cfg['data']['host'],
        port=cfg['data']['port'],
        database=cfg['data']['name']
    )
