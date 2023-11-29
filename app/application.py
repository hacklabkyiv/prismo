from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from flask import Flask, render_template, jsonify, request, redirect, url_for

import logging
import threading
import time
from logging.handlers import RotatingFileHandler


# New
from models.device import Device
from models.user import User
from models.access_log import AccessLog

from api.web_api import web_api
from api.device_api import device_api

app = Flask(__name__)
app.register_blueprint(web_api)
app.register_blueprint(device_api)


app.config["SECRET_KEY"] = "secret_key"
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
    return render_template("prismo/devices.html")


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
