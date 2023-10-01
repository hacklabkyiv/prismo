import logging
import os
import sys
from dataclasses import dataclass
from typing import List

import psycopg2 as psycopg
import yaml

from app.data.permissions_repository import get_user_permissions
from app.data.user_repository import get_all_users

try:
    from yaml import CLoader as Loader, CDumper
except ImportError:
    from yaml import Loader

# Configuration file
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.cfg')

try:
    cfg = yaml.load(open(CONFIG_FILE, 'r'), Loader=Loader)
except IOError as e:
    logging.error("Config file not found!")
    logging.error("Exception: %s" % str(e))
    sys.exit(1)


@dataclass
class Device:
    device_key: str
    device_name: str

    def __init__(self, device_key, device_name):
        self.device_key = device_key
        self.device_name = device_name


def get_devices():
    with psycopg.connect(user=cfg['data']['user'],
                         password=cfg['data']['password'],
                         host=cfg['data']['host'],
                         port=cfg['data']['port'],
                         database=cfg['data']['name']) as connection:
        with connection.cursor() as cur:
            cur.execute("SELECT id, name FROM devices order by name")
            rows = cur.fetchall()

            devices = []
            for row in rows:
                device_id, device_name = row
                device = Device(device_id, device_name)
                devices.append(device)

        connection.commit()

    return devices


@dataclass()
class PermissionUiModel:
    isGranted: bool
    device_key: str


@dataclass
class AccessControlPanelRow:
    user_name: str
    user_key: str
    last_enter: str
    permissions: List[PermissionUiModel]

    def __init__(self, user_name, user_key, last_enter, permissions):
        self.user_name = user_name
        self.user_key = user_key
        self.last_enter = last_enter
        self.permissions = permissions


@dataclass
class AccessControlPanel:
    header: List[str]
    rows: List[AccessControlPanelRow]

    def __init__(self, header, rows):
        self.header = header
        self.rows = rows


def get_access_control_panel():
    users = get_all_users()
    devices = get_devices()

    header = ['User name', 'User key', 'Last enter']
    for device in devices:
        header.append(device.device_name)

    rows = []

    for user in users:
        access_control_panel_row = build_user_permissions_row(user, devices)
        rows.append(access_control_panel_row)

    return AccessControlPanel(header, rows)


def build_user_permissions_row(user, devices):
    grated_user_device = get_user_permissions(user.user_key)
    user_permissions_ui_models = []
    for device in devices:
        permission_model = PermissionUiModel(device.device_key in grated_user_device, device.device_key)
        user_permissions_ui_models.append(permission_model)

    return AccessControlPanelRow(user.user_name, user.user_key, user.last_enter,
                                 user_permissions_ui_models)
