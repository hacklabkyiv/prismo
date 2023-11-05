import flask_login
from flask import Blueprint, request, render_template

from app.config import set_setting, key_slack_token, key_slack_backup_channel, get_setting
from app.features.backup_database import backup_data_base

settings_blue_print = Blueprint('settings', __name__)


@settings_blue_print.route('/settings', methods=['GET', 'POST'])
@flask_login.login_required
def index():
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

    return render_template('settings.html', settings=settings)


@settings_blue_print.route('/send-backup-to-slack', methods=['POST'])
@flask_login.login_required
def send_backup_to_slack():
    print("Sending backup to slack")
    backup_data_base()
    return 'OK'
