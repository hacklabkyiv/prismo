import json
import logging
import os
import sys
from pathlib import Path

import yaml

try:
    from yaml import CLoader as Loader, CDumper
except ImportError:
    from yaml import Loader

# Configuration file
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../config.cfg')

# Initial setup
try:
    cfg = yaml.load(open(CONFIG_FILE, 'r'), Loader=Loader)
except IOError as e:
    logging.error("Config file not found!")
    logging.error("Exception: %s" % str(e))
    sys.exit(1)

database_file = Path("database.db")

UPLOAD_FOLDER = '/uploads'

internal_config_file = Path("internal_config.json")
_slat_key = 'slat'


def get_slat():
    with open(internal_config_file, 'r') as config_file:
        config = json.load(config_file)
        return config[_slat_key]


def set_slat(slat):
    _update_config_field(_slat_key, slat)


def _update_config_field(key: str, value: str):
    if not internal_config_file.is_file():
        with open(internal_config_file, 'w') as config_file:
            json.dump({}, config_file, indent=4)
            config_file.close()

    with open(internal_config_file, 'r') as config_file:
        config = json.load(config_file)
        config_file.close()

    config[key] = value

    with open(internal_config_file, 'w') as config_file:
        json.dump(config, config_file, indent=4)
        config_file.close()
