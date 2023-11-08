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
    logging.error("Exception: %s", str(e))
    sys.exit(1)

database_file = Path("database.db")

UPLOAD_FOLDER = '/uploads'

internal_config_file = Path("internal_config.json")
slat_key = 'slat'
key_slack_token = 'key_slack_token'
key_slack_backup_channel = 'key_slack_backup_channel'
key_secret_key = 'key_secret_key'
key_database_version = 'key_database_version'


def get_setting(key: str):
    with open(internal_config_file, 'r') as config_file:
        config = json.load(config_file)
        config_file.close()
        return config.get(key, None)


def set_setting(key: str, value: str):
    with open(internal_config_file, 'r') as config_file:
        config = json.load(config_file)
        config_file.close()

    config[key] = value

    with open(internal_config_file, 'w') as config_file:
        json.dump(config, config_file, indent=4)
        config_file.close()


def create_internal_config_file():
    if not internal_config_file.is_file():
        with open(internal_config_file, 'w') as config_file:
            json.dump({
                key_database_version: 1,
            }, config_file, indent=4)
            config_file.close()
