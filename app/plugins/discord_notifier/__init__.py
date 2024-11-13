"""
Discord Notifier Plugin
======================
Notify members about tools and doors usage statistics in Discord

How to use?
-----------
1. Setup WebHooks for your channel.
HOWTO: https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
2. Create new branch in settings, e.g:
 "PLUGINS": {
            "slack_notifier": {
                "SLACK_DOOR_CHANNEL": "#prismo-door-channel",
                "SLACK_TOKEN": "xoxb-this-is-not-areal-slack-token",
                "SLACK_TOOL_CHANNEL": "#prismo-debug"
            },
            "discord_notifier": {
                "DISCORD_DOOR_EVENT_WEBHOOK": "https://discord.com/api/webhooks/your-webhook"
            },
"""
from flask import Flask

from .discord_notifier import DiscordNotifierPlugin


def init_plugin(app: Flask):
    DiscordNotifierPlugin(app.app_context())
