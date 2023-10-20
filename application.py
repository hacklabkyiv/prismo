import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request
from flask_sock import Sock

from app.config import cfg
from app.data.device_repository import get_full_device, get_all_devices, add_device
from app.data.permissions_repository import grant_permission, reject_permission, get_user_with_permission_to_device
from app.data.user_repository import delete_user, add_user, get_full_user
from app.data.work_logs_repository import start_work, finish_work, get_full_logs, get_latest_key
from app.slack.slack_sender import send_user_enter
from users_view_model import get_access_control_panel
from app.utils.fimware_updater import update_firmware_full

app = Flask(__name__)
websocket = Sock(app)
app.config['SECRET_KEY'] = 'secret!'
logger = logging.getLogger(__name__)

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


@app.route('/user', methods=['POST'])
def add_user_route():
    user_name = request.form['nick']
    user_key = request.form['key']
    add_user(user_name, user_key)
    return 'OK'


@app.route('/user', methods=['DELETE'])
def delete_user_route():
    user_key = request.form['user_key']
    delete_user(user_key)
    return 'OK'


@app.route('/device', methods=['POST'])
def add_device_route():
    device_id = request.form['device_id']
    device_name = request.form['device_name']
    add_device(device_id, device_name)
    return 'OK'

@app.route('/permission', methods=['POST'])
def grant_permission_route():
    user_key = request.form['user_key']
    permission = request.form['device_id']
    grant_permission(user_key, permission)
    return 'OK'


@app.route('/permission', methods=['DELETE'])
def reject_permission_route():
    user_key = request.form['user_key']
    permission = request.form['device_id']
    reject_permission(user_key, permission)
    return 'OK'


@app.route('/', methods=['GET'])
def index():
    access_control_panel = get_access_control_panel()
    latest_key = get_latest_key()
    logger.info('Access control panel data: %s' % access_control_panel)
    logger.info('Latest key: %s' % latest_key)

    return render_template("index.html", latest_key=latest_key, access_control_panel=access_control_panel)


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

"""
Prototype for firmware_update feature
"""
@websocket.route('/updater_socket')
def updater(websocket):
    update_firmware_full(websocket)