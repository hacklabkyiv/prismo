import json

from flask import Flask, render_template, request, redirect, url_for
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from pyee.base import EventEmitter

from api.device_api import device_api
from api.web_api import web_api
from models.admin_user import AdminUser
from plugins.slack_notifier import SlackNotifierPlugin

app = Flask(__name__)
app.ee = EventEmitter()

app.register_blueprint(web_api)
app.register_blueprint(device_api)

app.config.from_file("config_debug.json", load=json.load)

login_manager = LoginManager()
login_manager.init_app(app)

# Plugins
slack_notifier = SlackNotifierPlugin(app.app_context())


@login_manager.user_loader
def load_user(user_id):
    return AdminUser("", "")


@app.route("/init_app", methods=["GET", "POST"])
def init_app_route():
    if request.method == "GET":
        return render_template("auth/init_app.html")

    username = request.form["username"]
    password = request.form["password"]
    AdminUser(username, password).create_user()

    # if "file" in request.files:
    #    file = request.files["file"]
    # else:
    #    file = None

    # init_app(username, password, slat, file)

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users"))

    if request.method == "GET":
        return render_template("auth/login.html")

    username = request.form["username"]
    password = request.form["password"]

    user = AdminUser(username)
    if user is None or not user.check_password(password):
        app.logger.error("Auth failed: Invalid username or password")
        return render_template("auth/login.html", error="Invalid username or password")

    app.logger.info("Auth success: %s", username)
    login_user(user)
    return redirect(url_for("users"))


@app.route("/logout")
def logout():
    app.logger.info("Logout: %s", current_user.username)
    logout_user()
    return redirect(url_for("login"))


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
    return render_template("prismo/users.html")


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
    return render_template("prismo/settings.html")
