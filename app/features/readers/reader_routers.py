from flask import (
    Blueprint, request
)

from app.features.admin.init_app import get_db_connection
from app.features.permissions.permissions_repository import get_user_with_permission_to_device
from app.features.slack_notifier import send_dm_message

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

    if operation == 'unlock':
        send_log_of_last_usage(device_id, user_key)

    connection = get_db_connection()
    connection.execute(
        "INSERT INTO event_logs(device_id, user_key, operation_type) VALUES (?, ?, ?)",
        (device_id, user_key, operation)
    )
    connection.commit()
    return 'OK', 201


def send_log_of_last_usage(device_id, user_key):
    cursor = get_db_connection().cursor()
    cursor.execute(
        "SELECT slack_id, name, operation_time "
        "FROM event_logs "
        "JOIN users user ON event_logs.user_key = user.key "
        "WHERE device_id = ? and operation_type = 'unlock' "
        "ORDER BY operation_time DESC "
        "LIMIT 3", (device_id,)
    )
    rows = cursor.fetchall()
    message = "The last 3 people who unlocked the door were: \n"
    for row in rows:
        slack_id, name, operation_time = row
        if slack_id is None:
            message += f"{name} at {operation_time}\n"
        else:
            message += f"<@{slack_id}> at {operation_time}\n"

    send_dm_message(user_key, message)
