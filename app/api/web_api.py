from flask import Flask, Blueprint, jsonify, request
from flask_sock import Sock

from models.access_log import AccessLog
from models.user import User

web_api = Blueprint("web_api", __name__)


@web_api.route("/api/logs", methods=["GET"])
def api_get_logs():
    # Retrieve parameters from the query string
    start_time = request.args.get("start_time", default=None)
    end_time = request.args.get("end_time", default=None)
    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)

    return jsonify(AccessLog.get_full_log(start_time, end_time, limit, offset))


@web_api.route("/api/users", methods=["GET"])
def api_get_user_permissions():
    return jsonify(User.get_permissions())

# websocket = Sock(app)
# @websocket.route('/updater_socket')
# def updater(websocket):
#    # pylint: disable=redefined-outer-name
#    update_firmware_full(websocket)
