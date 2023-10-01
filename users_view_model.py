from dataclasses import dataclass
from typing import List

from app.data.database_driver import establish_connection
from app.data.permissions_repository import get_user_permissions
from app.data.user_repository import get_all_users


@dataclass
class Device:
    device_key: str
    device_name: str

    def __init__(self, device_key, device_name):
        self.device_key = device_key
        self.device_name = device_name


def get_devices():
    with establish_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM devices order by name")
            rows = cursor.fetchall()

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
