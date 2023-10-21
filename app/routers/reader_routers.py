from flask import (
    Blueprint
)

from app.data.permissions_repository import get_user_with_permission_to_device
from app.data.work_logs_repository import start_work, finish_work

reader_blue_print = Blueprint('readers', __name__, url_prefix='/readers')


@reader_blue_print.route('/user_with_access/<device_id>', methods=['GET'])
def users_with_access_to_device(device_id):
    return get_user_with_permission_to_device(device_id)


@reader_blue_print.route('/start_work/<user_key>/<device_id>', methods=['POST'])
def start_work_router(user_key, device_id):
    if start_work(user_key, device_id):
        return 'OK', 201
    else:
        return 'Device is already in use', 409


@reader_blue_print.route('/stop_work/<device_id>', methods=['POST'])
def finish_work_router(device_id):
    finish_work(device_id)
    return 'OK', 202
