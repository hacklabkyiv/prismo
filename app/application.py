from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_sock import Sock
from flask import Flask, render_template, jsonify, request, redirect, url_for

import logging
import threading
import time
from logging.handlers import RotatingFileHandler


# New
from models.device import Device
from models.user import User
from models.access_log import AccessLog

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret_key"
websocket = Sock(app)
logger = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

logging.basicConfig(level=logging.DEBUG)
# Create logger to be able to use rolling logs
logger.setLevel(logging.DEBUG)
# log_handler = RotatingFileHandler(cfg['logging']['logfile'], mode='a',
#                                  maxBytes=int(cfg['logging']['logsize_kb']) * 1024,
#                                  backupCount=int(cfg['logging']['rolldepth']),
#                                  delay=0)

log_handler = RotatingFileHandler(
    "log.txt", mode="a", maxBytes=100 * 1024, backupCount=int(5), delay=0
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

# noinspection PyBroadException
# @login_manager.user_loader
# def loader_user(user_id):
#    # pylint: disable=broad-exception-caught
#    try:
#        return get_flask_admin_user_by_id(user_id)
#    except Exception:
#        return None


# noinspection PyBroadException
# @login_manager.request_loader
# def request_loader(request):
#    # pylint: disable=broad-exception-caught
#    username = request.form.get('username')
#    try:
#        print(f"user name: {username}")
#        return get_flask_admin_user_by_user_name(username)
#    except Exception:
#        print(f"none: {username}")
#        return None

# Admin routes


class User(UserMixin):
    def __init__(self, username, password):
        self.username = ""
        self.password = ""
        self.id = 1

    def check_password(self, password):
        return True

    def is_authenticated(self):
        return True


@login_manager.user_loader
def load_user(user_id):
    return User("", "")


@app.route("/init_app", methods=["GET", "POST"])
def init_app_route():
    if request.method == "GET":
        return render_template("auth/init_app.html")

    username = request.form["username"]
    password = request.form["password"]
    slat = request.form["slat"]
    if "file" in request.files:
        file = request.files["file"]
    else:
        file = None

    # init_app(username, password, slat, file)

    return redirect(url_for("admin.login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users"))

    if request.method == "GET":
        return render_template("auth/login.html")

    username = request.form["username"]
    password = request.form["password"]

    user = User(username, password)
    if user is None or not user.check_password(password):
        return render_template("auth/login.html", error="Invalid username or password")

    login_user(user)
    return redirect(url_for("users"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


# App routes


@app.route("/", methods=["GET"])
def index():
    # if not database_file.is_file():
    #    return flask.redirect(flask.url_for('admin.init_app_route'))
    if current_user.is_authenticated:
        return redirect(url_for("users"))
    return redirect(url_for("login"))


@app.route("/users", methods=["GET"])
@login_required
def users():

    # Latest triggered key is used for new users registration.
    latest_triggered_key = Device.get_latest_key()
    logger.info("Latest triggered key: %s", latest_triggered_key)

    return render_template("prismo/users.html", latest_key=latest_triggered_key)


@app.route("/devices")
@login_required
def devices():
    devices = Device.get_all_devices()
    return render_template("prismo/devices.html", devices=devices)


@app.route("/logs")
@login_required
def logs():
    return render_template("prismo/logs.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """
    if request.method == 'POST':
        slack_token = request.form.get('slack_token')
        channel_id = request.form.get('channel_id')

        if slack_token is not None:
            set_setting(key_slack_token, slack_token)

        if channel_id is not None:
            set_setting(key_slack_backup_channel, channel_id)

    settings = {}
    saved_slack_token = get_setting(key_slack_token)

    if saved_slack_token is not None:
        settings['slack_token'] = get_setting(key_slack_token)

    saved_channel_id = get_setting(key_slack_backup_channel)
    if saved_channel_id is not None:
        settings['channel_id'] = get_setting(key_slack_backup_channel)
    """
    return render_template("prismo/settings.html", settings=settings)


"""
Routes and logic for REST API used by web application
"""

# TODO all API calls, including API for readers move to separate module.
@app.route("/api/logs", methods=["GET"])
def api_get_logs():
    # TODO: error handling, input data validation etc.
    # Retrieve parameters from the query string
    start_time = request.args.get("start_time", default=None)
    end_time = request.args.get("end_time", default=None)
    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)

    return jsonify(AccessLog.get_full_log(start_time, end_time, limit, offset))


@app.route("/api/users", methods=["GET"])
def api_get_user_permissions():
    return jsonify(User.get_permissions())


# @websocket.route('/updater_socket')
# def updater(websocket):
#    # pylint: disable=redefined-outer-name
#    update_firmware_full(websocket)


"""
Routes and logic for reader API
"""
