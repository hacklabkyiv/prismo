import slack_notifications as slack

from app.config import cfg
from app.data.user_repository import get_user

slack = slack.Slack(token=cfg['slack']['token'])


def send_notification(text: str):
    print("Send text: %s" % text)
    slack.send_notify(channel='test', username='TestNotification', text=text)


def send_user_enter(user_key: str):
    user = get_user(user_key)
    send_notification("%s enters to the door" % user.name)
