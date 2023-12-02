import flask_login
from flask import (
    Blueprint, render_template
)
from flask import request

from app.features.admin.init_app import get_db_connection
from app.features.slack_notifier import send_dm_message
from app.features.users.user_repository import delete_user, add_user, get_full_user

user_blue_print = Blueprint('users', __name__, url_prefix='/user')


@user_blue_print.route('/', methods=['POST'])
@flask_login.login_required
def add_user_route():
    user_name = request.form['nick']
    user_key = request.form['key']
    add_user(user_name, user_key)
    return 'OK'


@user_blue_print.route('/', methods=['DELETE'])
@flask_login.login_required
def delete_user_route():
    user_key = request.form['user_key']
    delete_user(user_key)
    return 'OK'


@user_blue_print.route('/<user_key>', methods=['GET', 'POST'])
def user_page(user_key):
    if request.method == 'POST':
        slack_id = request.form['slack_id']

        connection = get_db_connection()
        connection.execute(
            "UPDATE users SET slack_id=? WHERE key=?",
            (slack_id, user_key)
        )
        connection.commit()

    return render_template("user_page.html", full_user=get_full_user(user_key))


@user_blue_print.route('/send-test-message-to-user', methods=['POST'])
@flask_login.login_required
def send_test_message_to_dm():
    json = request.json
    user_key = json['user_key']
    send_dm_message(user_key, 'Test message')
    return 'OK'
