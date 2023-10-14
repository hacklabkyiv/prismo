from dataclasses import dataclass
from typing import List

from app.data.device_repository import get_all_devices
from app.data.permissions_repository import get_user_permissions
from app.data.user_repository import get_all_users, UserWithLastEnter


@dataclass()
class PermissionUiModel:
    isGranted: bool
    device_key: str

    def __init__(self, is_granted, device_key):
        self.isGranted = is_granted
        self.device_key = device_key


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


def get_access_control_panel() -> AccessControlPanel:
    users = get_all_users()
    devices = get_all_devices()

    header = ['User name', 'User key', 'Last enter']
    for device in devices:
        header.append(device.name)

    rows = []

    for user in users:
        access_control_panel_row = build_user_access_control_permissions_row(user, devices)
        rows.append(access_control_panel_row)

    return AccessControlPanel(header, rows)


def build_user_access_control_permissions_row(user: UserWithLastEnter, devices):
    grated_user_device = get_user_permissions(user.user.key)
    user_permissions_ui_models = []
    for device in devices:
        permission_model = PermissionUiModel(device.id in grated_user_device, device.id)
        user_permissions_ui_models.append(permission_model)

    return AccessControlPanelRow(user.user.name, user.user.key, user.last_enter,
                                 user_permissions_ui_models)
