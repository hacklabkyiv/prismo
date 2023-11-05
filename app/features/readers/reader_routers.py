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
    user_key = request.args['user_key']
    operation = request.args['operation']

    cursor = get_db_connection().cursor(
        "INSERT INTO event_logs(device_id, user_key, operation_type) VALUES (?, ?, ?)",
        (device_id, user_key, operation)
    )
    cursor.execute()
    return 'OK', 201
