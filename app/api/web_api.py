# pylint: disable=consider-using-f-string
# pylint: disable=broad-except
import json

from flask import Blueprint, jsonify, request
from flask import current_app as app
from models.access_log import AccessLog
from models.device import Device
from models.user import User

web_api = Blueprint("web_api", __name__)


# Logs API


@web_api.route("/api/logs", methods=["GET"])
def api_get_logs():
    # Retrieve parameters from the query string
    start_time = request.args.get("start_time", default=None)
    end_time = request.args.get("end_time", default=None)
    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)

    return jsonify(AccessLog.get_full_log(start_time, end_time, limit, offset))


# Devices API


@web_api.route("/api/devices/latest_key", methods=["GET"])
def api_get_latest_key():
    return jsonify(Device.get_latest_key())


@web_api.route("/api/devices", methods=["GET"])
def api_get_devices():
    return jsonify(Device.get_all_devices())


@web_api.route("/api/devices", methods=["POST"])
def api_add_device():
    device_data = request.get_json()

    try:
        device = Device(device_data["device_id"], device_data.get(
            "device_name"), device_data["device_type"])
        device.save()
        app.logger.info("Device %s added successfully" % device_data["device_id"])
        return jsonify({"message": "Device added successfully"}), 201
    except Exception as e:
        app.logger.error("Error adding device: %s" % e)
        return jsonify({"message": "Error adding device"}), 303


@web_api.route("/api/devices/<device_id>", methods=["PUT"])
def api_update_device(device_id):
    device_data = request.get_json()

    device = Device(device_id=device_id, device_type=None, name=None)
    device.update_device(device_data.get("device_type", None), device_data.get("name", None))

    return jsonify({"message": "Device updated successfully"})


@web_api.route("/api/devices/<device_id>", methods=["DELETE"])
def api_remove_device(device_id):
    try:
        device = Device(device_id=device_id, device_type=None, name=None)
        device.delete()
        app.logger.info("Device %s removed successfully" % device_id)
        return jsonify({"message": "Device removed successfully"}), 200
    except Exception as e:
        app.logger.error("Error removing device: %s" % e)
        return jsonify({"message": "Error removing device"}), 303


# Users API

@web_api.route("/api/users", methods=["GET"])
def api_get_user_permissions():
    return jsonify(User.get_permissions())


@web_api.route("/api/users", methods=["POST"])
def api_add_user():
    user_data = request.get_json()
    user = User(user_data["name"], user_data["email"], user_data["phone"], user_data["key"])

    number_of_new_user_added = user.save()

    # pylint: disable=no-else-return
    if number_of_new_user_added == 1:
        return jsonify({"message": "User added successfully"}), 201
    elif number_of_new_user_added == 0:
        return jsonify({"message": "User already exists"}), 303

    # Handle other cases (e.g., database error)
    return jsonify({"message": "An error occurred"}), 500


@web_api.route("/api/users/<user_key>", methods=["DELETE"])
def api_delete_user(user_key):
    user = User(key=user_key, name=None, email=None, phone=None)
    user.delete()

    return jsonify({"message": "User deleted successfully"})


@web_api.route("/api/users/<user_key>/devices/<device_id>", methods=["POST"])
def api_add_user_permission(user_key, device_id):
    user = User(key=user_key, name=None, email=None, phone=None)
    user.add_permission(device_id)

    return jsonify({"message": "User permission added successfully"})


@web_api.route("/api/users/<user_key>/devices/<device_id>", methods=["DELETE"])
def api_remove_user_permission(user_key, device_id):
    user = User(key=user_key, name=None, email=None, phone=None)
    user.remove_permission(device_id)

    return jsonify({"message": "User permission removed successfully"})


# Settings API


@web_api.route("/api/settings", methods=["GET"])
def api_get_settings():
    """
    Returns the current settings of the system.

    Returns:
        dict: The current settings of prismo.

    Example:
        {
            "device_type": "printer",
            "name": "Printer 1"
        }

    Raises:
        Exception: If the settings cannot be retrieved.

    """
    try:
        settings = app.config["PRISMO"]
        app.logger.info("Retrieved settings: %s", settings)
        return jsonify(settings)
    except Exception as e:
        app.logger.error("Error retrieving settings: %s", e)
        raise Exception("Error retrieving settings") from e


@web_api.route("/api/settings", methods=["PUT"])
def api_update_settings():
    """
    Updates the current settings of the system.

    Returns:
        dict: The updated settings.
    """

    try:
        settings = app.config["PRISMO"]
        new_settings = json.loads(request.data)
        app.logger.info("New settings received: %s", new_settings)
        app.config["PRISMO"] = new_settings

        app.logger.info("Updated settings: %s", settings)
        # Update "PRISMO" branch in settings file
        try:
            with open(app.config["CURRENT_CONFIG_FILE"], "r") as f:
                stored_settings = json.load(f)
            with open(app.config["CURRENT_CONFIG_FILE"], "w") as f:
                stored_settings["PRISMO"] = new_settings
                json.dump(stored_settings, f, indent=4)
                app.logger.warning("Settings updated, new settings are: %s", stored_settings)
        except Exception as e:
            app.logger.error("Error saving settings to file: %s", e)

        return jsonify(settings)
    except Exception as e:
        app.logger.error("Error updating settings: %s", e)
        raise Exception("Error updating settings") from e
