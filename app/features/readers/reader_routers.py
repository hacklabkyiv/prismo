from flask import (
    Blueprint, request
)

from app.features.admin.init_app import get_db_connection
from app.features.permissions.permissions_repository import get_user_with_permission_to_device

reader_blue_print = Blueprint('reader', __name__, url_prefix='/reader')


@reader_blue_print.route('/<device_id>/accesses/', methods=['GET'])
def accesses(device_id):
    return {
        'keys': get_user_with_permission_to_device(device_id)
    }


@reader_blue_print.route('/<device_id>/log_operation', methods=['POST'])
def log_operation(device_id):
    json = request.json

    operation = json['operation']

    if operation not in ['lock', 'unlock']:
        raise Exception('Invalid operation')

    data = json.get('data')
    if data is None:
        user_key = None
    else:
        user_key = data['key']

    if (operation == 'unlock') and user_key is None:
        raise Exception('Invalid operation')

    connection = get_db_connection()
    connection.execute(
        "INSERT INTO event_logs(device_id, user_key, operation_type) VALUES (?, ?, ?)",
        (device_id, user_key, operation)
    )
    connection.commit()
    return 'OK', 201
