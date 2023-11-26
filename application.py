import logging
import threading
import time
from logging.handlers import RotatingFileHandler

import flask
import flask_login
import schedule
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sock import Sock
from flask import jsonify, request

from app.config import cfg, UPLOAD_FOLDER, get_setting, key_secret_key, set_setting, \
    create_internal_config_file
from app.data.work_logs_repository import get_latest_key
from app.features.admin.admin_routrers import admin_blue_print
from app.features.admin.admins_repository import get_admin_user_by_flask_user, \
    get_flask_admin_user_by_id, \
    get_flask_admin_user_by_user_name
from app.features.admin.init_app import database_file
from app.features.backup_database import backup_data_base
from app.features.permissions.access_pannel import get_access_control_panel
from app.features.permissions.permission_routers import permissions_blue_print
from app.features.readers.manage_device import manage_device_blue_print
from app.features.readers.reader_routers import reader_blue_print
from app.routers.settings_routers import settings_blue_print
from app.features.users.user_routers import user_blue_print
from app.utils.fimware_updater import update_firmware_full

from app.data.work_logs_repository import query_event_logs

app = Flask(__name__)

create_internal_config_file()

secret_key = get_setting(key_secret_key)

app.config['SECRET_KEY'] = secret_key
websocket = Sock(app)
logger = logging.getLogger(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)

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

#app.register_blueprint(reader_blue_print)
#app.register_blueprint(permissions_blue_print)
app.register_blueprint(user_blue_print)
app.register_blueprint(admin_blue_print)
#app.register_blueprint(settings_blue_print)
#app.register_blueprint(manage_device_blue_print)


#def scheduler_thread():
#    while True:
#        schedule.run_pending()
#        time.sleep(1)


#schedule.every().day.at("22:17").do(backup_data_base)

#scheduler = threading.Thread(target=scheduler_thread)
#scheduler.daemon = True
#scheduler.start()


# noinspection PyBroadException
@login_manager.user_loader
def loader_user(user_id):
    # pylint: disable=broad-exception-caught
    try:
        return get_flask_admin_user_by_id(user_id)
    except Exception:
        return None


# noinspection PyBroadException
@login_manager.request_loader
def request_loader(request):
    # pylint: disable=broad-exception-caught
    username = request.form.get('username')
    try:
        print(f"user name: {username}")
        return get_flask_admin_user_by_user_name(username)
    except Exception:
        print(f"none: {username}")
        return None


@app.route('/', methods=['GET'])
def index():
    if not database_file.is_file():
        return flask.redirect(flask.url_for('admin.init_app_route'))
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('users'))
    return flask.redirect(flask.url_for('admin.login'))


@app.route('/users', methods=['GET'])
@flask_login.login_required
def users():
    access_control_panel = get_access_control_panel()
    latest_key = get_latest_key()

    user = get_admin_user_by_flask_user(flask_login.current_user)
    if user is None:
        current_username = "Anonymous"
    else:
        current_username = user.username

    logger.info('Access control panel data: %s', access_control_panel)
    logger.info('Latest key: %s', latest_key)

    return render_template("users.html",
                           latest_key=latest_key,
                           access_control_panel=access_control_panel,
                           current_user=current_username)

@app.route('/devices')
@flask_login.login_required
def devices():
    return render_template('devices.html')

@app.route('/logs')
@flask_login.login_required
def logs():
    return render_template('logs.html')

@app.route('/settings', methods=['GET', 'POST'])
@flask_login.login_required
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
    return render_template('settings.html', settings=settings)


"""
Routes and logic for REST API used by web application
"""

# TODO all API calls, including API for readers move to separate module.
@app.route('/api/logs', methods=['GET'])
def api_get_logs():
    # TODO: error handling, input data validation etc.
    # Retrieve parameters from the query string
    start_time = request.args.get('start_time', default=None)
    end_time = request.args.get('end_time', default=None)
    limit = request.args.get('limit', default=100, type=int)
    offset = request.args.get('offset', default=0, type=int)

    return jsonify(query_event_logs(start_time, end_time, limit, offset))


@websocket.route('/updater_socket')
def updater(websocket):
    # pylint: disable=redefined-outer-name
    update_firmware_full(websocket)


"""
Routes and logic for reader API
"""