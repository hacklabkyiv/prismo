from flask import Blueprint, request

from app.features.admin.init_app import get_db_connection
from app.features.permissions.permissions_repository import (
    get_user_with_permission_to_device,
)
from app.features.slack_notifier import send_dm_message, send_channel_message

import json

reader_blue_print = Blueprint("reader", __name__, url_prefix="/reader")


@reader_blue_print.route("/<device_id>/accesses/", methods=["GET"])
def accesses(device_id):
    return {"keys": get_user_with_permission_to_device(device_id)}


@reader_blue_print.route("/<device_id>/log_operation", methods=["POST"])
def log_operation(device_id):

    json_data = json.loads(request.get_json())

    operation = json_data["operation"]
    if operation not in ["lock", "unlock", "deny_access"]:
        raise Exception("Invalid operation")

    try:
        user_key = json_data["key"]
    except KeyError:
        user_key = None

    if (operation == "unlock") and user_key is None:
        raise Exception("Invalid operation")

    if operation == "unlock":
        send_log_of_last_usage(device_id, user_key)
        send_message_of_unlocking(device_id, user_key)

    if operation == "lock":
        send_message_of_locking(device_id)

    connection = get_db_connection()
    connection.execute(
        "INSERT INTO event_logs(device_id, user_key, operation_type) VALUES (?, ?, ?)",
        (device_id, user_key, operation),
    )
    connection.commit()
    return "OK", 201


def send_message_of_locking(device_id):
    cursor = get_db_connection().cursor()
    cursor.execute(
        "SELECT slack_channel_id, name FROM devices WHERE id=?", (device_id,)
    )
    slack_channel_id, device_name, = cursor.fetchall()[0]
    if slack_channel_id is None:
        raise Exception("No slack channel id for device " + device_id)

    message = f"The {device_name} is free now"

    send_channel_message(slack_channel_id, message)


def send_message_of_unlocking(device_id, user_key):
    cursor = get_db_connection().cursor()
    cursor.execute(
        "SELECT slack_channel_id, name FROM devices WHERE id=?", (device_id,)
    )
    slack_channel_id, device_name, = cursor.fetchall()[0]
    if slack_channel_id is None:
        raise Exception("No slack channel id for device " + device_id)

    user_cursor = get_db_connection().cursor()
    user_cursor.execute("SELECT slack_id, name FROM users WHERE key=?", (user_key,))
    slack_id, user_name = user_cursor.fetchall()[0]
    if slack_id is None:
        message = f"{user_name} start using the {device_name}"
    else:
        message = f"<@{slack_id}> start using the {device_name}"

    send_channel_message(slack_channel_id, message)


def send_log_of_last_usage(device_id, user_key):
    cursor = get_db_connection().cursor()
    cursor.execute(
        "SELECT slack_id, name, operation_time "
        "FROM event_logs "
        "JOIN users user ON event_logs.user_key = user.key "
        "WHERE device_id = ? and operation_type = 'unlock' "
        "ORDER BY operation_time DESC "
        "LIMIT 3",
        (device_id,),
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
