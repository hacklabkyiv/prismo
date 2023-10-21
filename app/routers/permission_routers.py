import flask_login
from flask import Blueprint, request

from app.data.permissions_repository import grant_permission, reject_permission

permissions_blue_print = Blueprint('permission', __name__, url_prefix='/permission')


@permissions_blue_print.route('', methods=['POST'])
@flask_login.login_required
def grant_permission_route():
    user_key = request.form['user_key']
    permission = request.form['device_id']
    grant_permission(user_key, permission)
    return 'OK'


@permissions_blue_print.route('', methods=['DELETE'])
@flask_login.login_required
def reject_permission_route():
    user_key = request.form['user_key']
    permission = request.form['device_id']
    reject_permission(user_key, permission)
    return 'OK'
