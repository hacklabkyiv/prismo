import sqlite3
from discord import SyncWebhook

# pylint: disable=consider-using-f-string

class DiscordNotifierPlugin:
    def __init__(self, app_context):
        try:
            self.app_context = app_context
            self.logger = self.app_context.app.logger
            self.ee = self.app_context.app.ee  # Event emitter, used for event-based communication
            self.config = self.app_context.app.config["PRISMO"]["PLUGINS"]["discord_notifier"]
            self.db_uri = self.app_context.app.config["DATABASE_URI"]
            self.ee.add_listener('access-log-entry-added', self.access_log_entry_added)
            self.app_context.app.logger.info("Discord Notifier Plugin initialized")
        except Exception as e:
            self.logger.error("Error in DiscordNotifierPlugin.__init__: %s", e)
            raise e

    def get_user_name(self, user_key):
        """
        Get user name and id based on user key info
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
                    text_message = "🔩**%s** was unlocked by **%s**" % (device_name, user_name)
                    webhook = SyncWebhook.from_url(self.config["DISCORD_TOOL_EVENT_WEBHOOK"])
                    webhook.send(text_message)

                elif device_type == "door":
                    self.logger.info("Door opened: %s", device_name)
                    text_message = "🔐**%s** was opened by **%s**" % (device_name, user_name)
                    webhook = SyncWebhook.from_url(self.config["DISCORD_DOOR_EVENT_WEBHOOK"])
                    webhook.send(text_message)
                else:
                    self.logger.error("Unknown reader type! %s", device_type)

        except Exception as e:
            self.logger.error("Error in DiscordNotifierPlugin.access_log_entry_added: %s", e)
            raise e
