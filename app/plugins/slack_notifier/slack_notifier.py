import sqlite3
from datetime import datetime

from slack_bolt import App


# pylint: disable=consider-using-f-string


def unlock_message_block_constructor(tool, user):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🔓 * %s Tool was unlocked*" % tool,
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*User:*\n<example.com|%s>" % user
                },
                {
                    "type": "mrkdwn",
                    "text": "*When:*\n %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Total time used:*\n16.0 (2 days)"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Remaining balance:*\n32.0 hours (4 days)"
                }
            ]
        }]


def door_message_block_constructor(door, user):
    return [
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "emoji",
                            "name": "door",
                            "unicode": "1f6aa"
                        },
                        {
                            "type": "text",
                            "text": "  "
                        },
                        {
                            "type": "text",
                            "text": "%s" % user,
                            "style": {
                                "bold": True
                            }
                        },
                        {
                            "type": "text",
                            "text": " entered through the "
                        },
                        {
                            "type": "text",
                            "text": "%s" % door,
                            "style": {
                                "bold": True
                            }
                        }
                    ]
                }
            ]
        }
    ]


class SlackNotifierPlugin:
    def __init__(self, app_context):
        # Configure the Slack client with your token
        try:
            self.app_context = app_context
            self.logger = self.app_context.app.logger
            self.ee = self.app_context.app.ee  # Event emitter, used for event-based communication
            self.config = self.app_context.app.config["PRISMO"]["PLUGINS"]["slack_notifier"]
            self.db_uri = self.app_context.app.config["DATABASE_URI"]
            self.ee.add_listener('access-log-entry-added', self.access_log_entry_added)
            self.ee.add_listener('device-updated-keys', self.device_updated_keys)
            self.slack_app = App(token=self.config["SLACK_TOKEN"])
            self.app_context.app.logger.info("SlackNotifierPlugin initialized")
        except Exception as e:
            self.logger.error("Error in SlackNotifierPlugin.__init__: %s", e)
            raise e

    def get_user_name(self, user_key):
        """
        Get user name and slack id based on user key info
        """
        connection = sqlite3.connect(self.db_uri)
        cursor = connection.cursor()

        cursor.execute("SELECT name from users WHERE key = ?",
                       (user_key,),
                       )
        connection.commit()
        result = cursor.fetchone()

        connection.close()
        if result:
            return result[0]

        return None

    def get_device_name(self, device_id):
        """
        Get device name based on its ID
        """
        connection = sqlite3.connect(self.db_uri)
        cursor = connection.cursor()

        cursor.execute("SELECT name from devices WHERE id = ?",
                       (device_id,),
                       )
        connection.commit()
        result = cursor.fetchone()

        connection.close()
        if result:
            return result[0]

        return None

    def get_device_type(self, device_id):
        """
        Get device name based on its ID
        """
        connection = sqlite3.connect(self.db_uri)
        cursor = connection.cursor()

        cursor.execute("SELECT type from devices WHERE id = ?",
                       (device_id,),
                       )
        connection.commit()
        result = cursor.fetchone()

        connection.close()
        if result:
            return result[0]

        return None

    def access_log_entry_added(self, event):
        try:
            if event["operation"] == "unlock":
                user_name = self.get_user_name(event["user_key"])
                device_name = self.get_device_name(event["device_id"])
                device_type = self.get_device_type(event["device_id"])
                self.logger.info("Access log entry added")
                self.logger.info("User name: %s", user_name)
                if device_type == "tool":
                    self.logger.info("Device name: %s", device_name)
                    text_message = "🔓 * %s Tool was unlocked* by %s" % (device_name, user_name)
                    blocks = unlock_message_block_constructor(device_name, user_name)
                    self.slack_app.client.chat_postMessage(
                        channel=self.config["SLACK_TOOL_CHANNEL"],
                        text=text_message,
                        blocks=blocks)
                elif device_type == "door":
                    self.logger.info("Door opened: %s", device_name)
                    text_message = "🔓 * %s Door opened by * by %s" % (device_name, user_name)
                    blocks = door_message_block_constructor(device_name, user_name)
                    self.slack_app.client.chat_postMessage(
                        channel=self.config["SLACK_DOOR_CHANNEL"],
                        text=text_message,
                        blocks=blocks)
                else:
                    self.logger.error("Unknown reader type! %s", device_type)

        except Exception as e:
            self.logger.error("Error in SlackNotifierPlugin.access_log_entry_added: %s", e)
            raise e

    # pylint: disable=unused-argument
    def device_updated_keys(self, event):
        self.logger.info("Device updated keys event received")
