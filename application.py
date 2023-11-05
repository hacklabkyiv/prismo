import logging
import secrets
import threading
import time
from logging.handlers import RotatingFileHandler

import flask
import flask_login
import schedule
from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_sock import Sock

from app.backup_database import backup_data_base
from app.config import cfg, UPLOAD_FOLDER, get_setting, key_secret_key, set_setting
from app.data.device_repository import get_full_device, get_all_devices, add_device
from app.data.work_logs_repository import get_full_logs, get_latest_key
from app.features.admin.admin_routrers import admin_blue_print
from app.features.admin.admins_repository import get_admin_user_by_flask_user, \
    get_flask_admin_user_by_id, \
    get_flask_admin_user_by_user_name
from app.features.admin.init_app import database_file
from app.features.permissions.access_pannel import get_access_control_panel
from app.features.permissions.permission_routers import permissions_blue_print
from app.features.readers.reader_routers import reader_blue_print
from app.routers.settings_routers import settings_blue_print
from app.routers.user_routers import user_blue_print
from app.utils.fimware_updater import update_firmware_full

app = Flask(__name__)

secret_key = get_setting(key_secret_key)
if (secret_key is None) or (secret_key == ""):
    secret_key = secrets.token_hex(32)
    set_setting(key_secret_key, secret_key)

app.config['SECRET_KEY'] = secret_key
websocket = Sock(app)
logger = logging.getLogger(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)

if cfg['logging']['debug'] is True:
    app.config['DEBUG'] = True
    logging.basicConfig(level=logging.DEBUG)
    # Create logger to be able to use rolling logs
    logger.setLevel(logging.DEBUG)
    log_handler = RotatingFileHandler(cfg['logging']['logfile'], mode='a',
                                      maxBytes=int(cfg['logging']['logsize_kb']) * 1024,
                                      backupCount=int(cfg['logging']['rolldepth']),
                                      delay=0)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

app.register_blueprint(reader_blue_print)
app.register_blueprint(permissions_blue_print)
app.register_blueprint(user_blue_print)
app.register_blueprint(admin_blue_print)
app.register_blueprint(settings_blue_print)


def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at("22:17").do(backup_data_base)

scheduler = threading.Thread(target=scheduler_thread)
scheduler.daemon = True
scheduler.start()


# noinspection PyBroadException
@login_manager.user_loader
def loader_user(user_id):
    try:
        return get_flask_admin_user_by_id(user_id)
    except Exception:
        return None


# noinspection PyBroadException
@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    try:
        print("user name: %s" % username)
        return get_flask_admin_user_by_user_name(username)
    except Exception:
        print("none: %s" % username)
        return None


@app.route('/', methods=['GET'])
def index():
    if not database_file.is_file():
        return flask.redirect(flask.url_for('admin.init_app_route'))
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('access_panel'))
    else:
        return flask.redirect(flask.url_for('admin.login'))


@app.route('/device', methods=['POST'])
@flask_login.login_required
def add_device_route():
    device_id = request.form['device_id']
    device_name = request.form['device_name']
    add_device(device_id, device_name)
    return 'OK'


@app.route('/access_panel', methods=['GET'])
def access_panel():
    access_control_panel = get_access_control_panel()
    latest_key = get_latest_key()

    user = get_admin_user_by_flask_user(flask_login.current_user)
    if user is None:
        current_username = "Anonymous"
    else:
        current_username = user.username

    logger.info('Access control panel data: %s' % access_control_panel)
    logger.info('Latest key: %s' % latest_key)

    return render_template("access_panel.html",
                           latest_key=latest_key,
                           access_control_panel=access_control_panel,
                           current_user=current_username)


@app.route('/full_log_view')
def full_log_view():
    return render_template('full_log_view.html', logs=get_full_logs())


@app.route('/devices')
def devices():
    return render_template('devices.html', devices=get_all_devices())


@app.route("/device/<device_id>", methods=["GET"])
def device_page(device_id):
    return render_template("device_page.html", full_device=get_full_device(device_id))


@websocket.route('/updater_socket')
def updater(websocket):
    update_firmware_full(websocket)
