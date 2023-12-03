from flask import Flask, Blueprint, jsonify, request

from models.access_log import AccessLog
from models.user import User
from models.device import Device
from flask import current_app as app
import json


device_api = Blueprint("device_api", __name__)


@device_api.route("/devices/<device_id>/accesses/", methods=["GET"])
def accesses(device_id):
    data = Device.get_authorized_users(device_id)
    app.ee.emit('device-updated-keys', {"device_id": device_id})
    return {"keys": data}


@device_api.route("/devices/<device_id>/log_operation", methods=["POST"])
def log_operation(device_id):

    #json_data = json.loads(request.get_json())
    json_data = request.get_json()
    if not json_data:
        raise Exception("Invalid request, no JSON data received")
    # logging.info("Received request: " + str(json_data))

    operation = json_data["operation"]
    if operation not in ["lock", "unlock", "deny_access"]:
        raise Exception("Invalid operation")

    user_key = json_data["key"]

    if (operation == "unlock") and user_key is None:
        raise Exception("Invalid operation")

    AccessLog.add(device_id, user_key, operation)
    app.ee.emit('access-log-entry-added', {"device_id": device_id, "user_key": user_key, "operation": operation})
    return "OK", 201
