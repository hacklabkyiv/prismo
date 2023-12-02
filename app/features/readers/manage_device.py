import flask_login
from flask import Blueprint, render_template, request

from app.features.admin.init_app import get_db_connection
from app.features.readers.device_repository import get_all_devices, get_full_device, add_device
from app.features.slack_notifier import send_channel_message

manage_device_blue_print = Blueprint('manage_device', __name__)


@manage_device_blue_print.route('/devices')
def devices():
    return render_template('devices.html', devices=get_all_devices())


@manage_device_blue_print.route("/device/<device_id>", methods=["GET", "POST"])
def device_page(device_id):
    if request.method == 'POST':
        slack_channel_id = request.form['slack_channel_id']

        connection = get_db_connection()
        connection.execute(
            "UPDATE devices SET slack_channel_id=? WHERE id=?",
            (slack_channel_id, device_id)
        )
        connection.commit()
    return render_template("device_page.html", full_device=get_full_device(device_id))


@manage_device_blue_print.route('/device', methods=['POST'])
@flask_login.login_required
def add_device_route():
    device_id = request.form['device_id']
    device_name = request.form['device_name']
    add_device(device_id, device_name)
    return 'OK'


@manage_device_blue_print.route('/send-test-message-to-channel', methods=['POST'])
@flask_login.login_required
def send_test_message_to_dm():
    json = request.json
    device_id = json['device_id']
    cursor = get_db_connection().cursor()
    cursor.execute("SELECT slack_channel_id, name FROM devices WHERE id=?", (device_id,))
    slack_channel_id, name, = cursor.fetchall()[0]
    if slack_channel_id is None:
        return 'No slack channel id for device ' + device_id

    send_channel_message(slack_channel_id, "Test message for device " + name)

    return 'OK'
