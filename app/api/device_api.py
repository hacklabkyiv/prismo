from flask import Flask, Blueprint, jsonify, request

from models.access_log import AccessLog
from models.user import User
from models.device import Device

import json


device_api = Blueprint("device_api", __name__)


@device_api.route("/devices/<device_id>/accesses/", methods=["GET"])
def accesses(device_id):
    data = Device.get_authorized_users(device_id)
    return {"keys": data}


@device_api.route("/devices/<device_id>/log_operation", methods=["POST"])
def log_operation(device_id):

    json_data = json.loads(request.get_json())

    # logging.info("Received request: " + str(json_data))

    operation = json_data["operation"]
    if operation not in ["lock", "unlock", "deny_access"]:
        raise Exception("Invalid operation")

    user_key = json_data["key"]

    if (operation == "unlock") and user_key is None:
        raise Exception("Invalid operation")

    # if operation == "unlock":
    #    send_log_of_last_usage(device_id, user_key)
    #    send_message_of_unlocking(device_id, user_key)

    # if operation == "lock":
    #    send_message_of_locking(device_id)
    AccessLog.add(device_id, user_key, operation)

    return "OK", 201
