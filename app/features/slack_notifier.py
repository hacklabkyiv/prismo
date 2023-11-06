import logging

from slack_sdk import WebClient

from app.config import get_setting, key_slack_token
from app.features.admin.init_app import get_db_connection


def send_dm_message(user_key, message):
    slack_token = get_setting(key_slack_token)
    connection = get_db_connection()
    row = connection.cursor().execute("SELECT slack_id FROM users WHERE key=?",
                                      (user_key,)).fetchall()
    if len(row) != 1:
        return 'No user with such key'
    slack_id = row[0][0]
    print("slack id", slack_id)

    if (slack_token is None) or (slack_id is None):
        return

    client = WebClient(token=slack_token)

    response = client.chat_postMessage(
        channel=slack_id,
        text=message,
    )

    logging.info(response)


def send_channel_message(channel_id, message):
    slack_token = get_setting(key_slack_token)
    if (slack_token is None) or (channel_id is None):
        return

    client = WebClient(token=slack_token)

    response = client.chat_postMessage(
        channel=channel_id,
        text=message,
    )

    logging.info(response)
