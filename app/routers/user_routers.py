import flask_login
from flask import (
    Blueprint
)
from flask import request

from app.data.user_repository import delete_user, add_user

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