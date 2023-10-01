import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from os.path import getmtime

import yaml
from flask import Flask, render_template, request

from app.data.log_repository import get_logs
from app.data.permissions_repository import grant_permission, reject_permission, get_user_with_permission_to_device
from app.data.user_repository import delete_user, add_user
from app.data.work_logs_repository import start_work, finish_work, get_full_logs
from users_view_model import get_access_control_panel

try:
    from yaml import CLoader as Loader, CDumper
except ImportError:
    from yaml import Loader

# Configuration file
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.cfg')

# Initial setup
try:
    cfg = yaml.load(open(CONFIG_FILE, 'r'), Loader=Loader)
except IOError as e:
    logging.error("Config file not found!")
    logging.error("Exception: %s" % str(e))
    sys.exit(1)

LATEST_KEY_FILE = cfg['data']['latest-key-file']

app = Flask(__name__)
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


def get_latest_key_info():
    try:
        with open(LATEST_KEY_FILE, 'r') as f:
            key_value = f.read()
    except FileNotFoundError:
        key_value = '<absent>'
    # Getting modification datetime
    try:
        mod_time = getmtime(LATEST_KEY_FILE)
        mod_time_converted = datetime.datetime.fromtimestamp(
            mod_time).strftime('%Y-%m-%d %H:%M:%S')
    except OSError:
        mod_time_converted = '<unknown>'
    return "%s updated at: %s" % (key_value, mod_time_converted)


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
    logger.info('Access control panel data: %s' % access_control_panel)

    return render_template('index.html', access_control_panel=access_control_panel,
                           latest_key_info=get_latest_key_info())


@app.route('/device/user_with_access/<device_id>', methods=['GET'])
def users_with_access_to_device(device_id):
    return get_user_with_permission_to_device(device_id)


@app.route('/device/start_work/<user_key>/<device_id>', methods=['POST'])
def start_work_router(user_key, device_id):
    start_work(user_key, device_id)
    return 'OK'


@app.route('/device/stop_work/<user_key>/<device_id>', methods=['POST'])
def finish_work_router(user_key, device_id):
    finish_work(user_key, device_id)
    return 'OK'


@app.route('/log_view')
def log_view():
    return render_template('log_view.html', logs=get_logs())


@app.route('/full_log_view')
def full_log_view():
    return render_template('full_log_view.html', logs=get_full_logs())
