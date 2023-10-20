import logging
from logging.handlers import RotatingFileHandler

import flask
import flask_login
from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_sock import Sock

from app.config import cfg
from app.data.admins_repository import get_admin_user_by_flask_user, get_flask_admin_user_by_id, \
    get_flask_admin_user_by_user_name, \
    get_flask_admin_user_by_credentials
from app.data.device_repository import get_full_device, get_all_devices, add_device
from app.data.permissions_repository import grant_permission, reject_permission, \
    get_user_with_permission_to_device
from app.data.user_repository import delete_user, add_user, get_full_user
from app.data.work_logs_repository import start_work, finish_work, get_full_logs, get_latest_key
from app.slack.slack_sender import send_user_enter
from app.utils.fimware_updater import update_firmware_full
from users_view_model import get_access_control_panel

app = Flask(__name__)
app.config['SECRET_KEY'] = cfg['app']['secret_key']
websocket = Sock(app)
logger = logging.getLogger(__name__)

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


@login_manager.user_loader
def loader_user(user_id):
    return get_flask_admin_user_by_id(user_id)


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    return get_flask_admin_user_by_user_name(username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')

    username = flask.request.form['username']
    password = flask.request.form['password']
    flask_admin_user = get_flask_admin_user_by_credentials(username, password)

    if flask_admin_user is None:
        return 'Bad login'
    else:
        flask_login.login_user(flask_admin_user)
        return flask.redirect(flask.url_for('index'))


@app.route('/user', methods=['POST'])
@flask_login.login_required
def add_user_route():
    user_name = request.form['nick']
    user_key = request.form['key']
    add_user(user_name, user_key)
    return 'OK'


@app.route('/user', methods=['DELETE'])
@flask_login.login_required
def delete_user_route():
    user_key = request.form['user_key']
    delete_user(user_key)
    return 'OK'


@app.route('/device', methods=['POST'])
@flask_login.login_required
def add_device_route():
    device_id = request.form['device_id']
    device_name = request.form['device_name']
    add_device(device_id, device_name)
    return 'OK'


@app.route('/permission', methods=['POST'])
@flask_login.login_required
def grant_permission_route():
    user_key = request.form['user_key']
    permission = request.form['device_id']
    grant_permission(user_key, permission)
    return 'OK'


@app.route('/permission', methods=['DELETE'])
@flask_login.login_required
def reject_permission_route():
    user_key = request.form['user_key']
    permission = request.form['device_id']
    reject_permission(user_key, permission)
    return 'OK'


@app.route('/', methods=['GET'])
def index():
    access_control_panel = get_access_control_panel()
    latest_key = get_latest_key()

    user = get_admin_user_by_flask_user(flask_login.current_user)
    if user is None:
        current_username = "Anonymous"
    else:
        current_username = user.username

    logger.info('Access control panel data: %s' % access_control_panel)
    logger.info('Latest key: %s' % latest_key)

    return render_template("index.html",
                           latest_key=latest_key,
                           access_control_panel=access_control_panel,
                           current_user=current_username
                           )


@app.route('/device/user_with_access/<device_id>', methods=['GET'])
def users_with_access_to_device(device_id):
    return get_user_with_permission_to_device(device_id)


@app.route('/device/start_work/<user_key>/<device_id>', methods=['POST'])
def start_work_router(user_key, device_id):
    if device_id == 'door':
        send_user_enter(user_key)

    start_work(user_key, device_id)
    return 'OK'


@app.route('/device/stop_work/<user_key>/<device_id>', methods=['POST'])
def finish_work_router(user_key, device_id):
    finish_work(user_key, device_id)
    return 'OK'


@app.route('/full_log_view')
def full_log_view():
    return render_template('full_log_view.html', logs=get_full_logs())


@app.route('/devices')
def devices():
    return render_template('devices.html', devices=get_all_devices())


@app.route('/user/<user_key>', methods=['GET'])
def user_page(user_key):
    return render_template("user_page.html", full_user=get_full_user(user_key))


@app.route("/device/<device_id>", methods=["GET"])
def device_page(device_id):
    return render_template("device_page.html", full_device=get_full_device(device_id))


@websocket.route('/updater_socket')
def updater(websocket):
    update_firmware_full(websocket)
