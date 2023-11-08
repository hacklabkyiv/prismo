import flask
import flask_login
from flask import Blueprint, render_template, request

from app.features.admin.admins_repository import get_flask_admin_user_by_credentials
from app.features.admin.init_app import init_app

admin_blue_print = Blueprint('admin', __name__)


@admin_blue_print.route('/init_app', methods=['GET', 'POST'])
def init_app_route():
    if request.method == 'GET':
        return render_template('init_app.html')

    username = request.form['username']
    password = request.form['password']
    slat = flask.request.form['slat']
    if 'file' in flask.request.files:
        file = request.files['file']
    else:
        file = None

    init_app(username, password, slat, file)

    return flask.redirect(flask.url_for('admin.login'))


@admin_blue_print.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')

    username = flask.request.form['username']
    password = flask.request.form['password']
    flask_admin_user = get_flask_admin_user_by_credentials(username, password)

    if flask_admin_user is None:
        return "Bad login"

    flask_login.login_user(flask_admin_user)
    return flask.redirect(flask.url_for('access_panel'))


@admin_blue_print.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('admin.login'))
