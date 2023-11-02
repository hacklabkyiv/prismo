import logging
from logging.handlers import RotatingFileHandler

import flask
import flask_login
from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_sock import Sock

from app.config import cfg, UPLOAD_FOLDER
from app.data.admins_repository import get_admin_user_by_flask_user, get_flask_admin_user_by_id, \
    get_flask_admin_user_by_user_name, \
    get_flask_admin_user_by_credentials
from app.data.device_repository import get_full_device, get_all_devices, add_device
from app.data.work_logs_repository import get_full_logs, get_latest_key
from app.init_app import database_file, init_app
from app.routers.permission_routers import permissions_blue_print
from app.routers.reader_routers import reader_blue_print
from app.routers.user_routers import user_blue_print
from app.utils.fimware_updater import update_firmware_full
from users_view_model import get_access_control_panel

app = Flask(__name__)
app.config['SECRET_KEY'] = cfg['app']['secret_key']
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
        return flask.redirect(flask.url_for('init_app_route'))
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('access_panel'))
    else:
        return flask.redirect(flask.url_for('login'))


@app.route('/init_app', methods=['GET', 'POST'])
def init_app_route():
    if flask.request.method == 'GET':
        return render_template('init_app.html')

    username = flask.request.form['username']
    password = flask.request.form['password']
    slat = flask.request.form['slat']
    if 'file' in flask.request.files:
        file = request.files['file']
    else:
        file = None

    init_app(username, password, slat, file)

    return flask.redirect(flask.url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')

    username = flask.request.form['username']
    password = flask.request.form['password']
    flask_admin_user = get_flask_admin_user_by_credentials(username, password)

    print("Admin user: %s" % flask_admin_user)

    if flask_admin_user is None:
        return "Bad login"
    else:
        flask_login.login_user(flask_admin_user)
        return flask.redirect(flask.url_for('access_panel'))


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))


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
