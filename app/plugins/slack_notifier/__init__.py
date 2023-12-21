"""
Slack Notifier Plugin
======================
Notify members about tools and doors usage statistics in specified channel.

How to use?
-----------
1. TODO: write docs how to setup slack APP
2. Get Slack API token. Go to your apps(https://api.slack.com/apps), select PRISMO Access System,
go to "Oauth and permissions", install to workspace and get token, which begins with "xoxb-" prefix.
3. Pass as parameter into settings branch ["NOTIFIER"]["SLACK_TOKEN"]. You can do this after
installation on settings page
4. Add your Slack app to specified channel.
"""
from flask import Flask

from .slack_notifier import SlackNotifierPlugin


def init_plugin(app: Flask):
    SlackNotifierPlugin(app.app_context())
