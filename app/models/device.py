import sqlite3


class Device:
    """Represents a device in the database."""

    def __init__(self, device_id, name, device_type, slack_channel_id):
        """Initializes a new device instance.

        Args:
            device_id (str): The unique identifier for the device.
            name (str): The name of the device.
            device_type (str): The type of device (e.g., "tool").
            slack_channel_id (str): The Slack channel ID for notifications about the device.
        """
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self.slack_channel_id = slack_channel_id

    @classmethod
    def get_all_devices(cls):
        """Fetches all devices from the database and returns them as dictionaries.

        Returns:
            List[dict]: A list of dictionaries representing the devices.
        """
        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM devices")
        devices_dict = cursor.fetchall()

        # Convert the results to a list of dictionaries
        result_dicts = [dict(row) for row in devices_dict]
        connection.close()
        return result_dicts

    @classmethod
    def get_authorized_users(cls, device_id):
        """
        Retrieves the list of authorized users for a specific device.
        
        Args:
            device_id (int): The ID of the device to check permissions for.
        
        Returns:
            list: A list of user keys authorized to access the specified device.
        """

        # Connect to the SQLite database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Fetch authorized users for the given device
        cursor.execute(
            "SELECT users.key FROM users INNER JOIN permissions ON users.key = permissions.user_key WHERE permissions.device_id = ?",
            (device_id,),
        )
        authorized_users = [row[0] for row in cursor.fetchall()]

        # Close the database connection
        conn.close()

        return authorized_users

    @classmethod
    def get_devices_ids_and_names(cls):
        # ""Fetches all device ids and names

        # Returns:
        #    List: A list of string of device names representing the devices.
        # "
        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM devices")
        devices = cursor.fetchall()

        connection.close()
        device_dict = {}
        for device in devices:
            device_id, device_name = device["id"], device["name"]
            device_dict[device_id] = device_name

        return device_dict

    @classmethod
    def save(cls, device):
        """Saves a device to the database.

        Args:
            device (dict): A dictionary containing the device data.
        """
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO devices (id, name, type, slack_channel_id)
            VALUES (?, ?, ?, ?)
        """,
            (device["id"], device["name"], device["type"], device["slack_channel_id"]),
        )
        connection.commit()
        connection.close()

    @classmethod
    def get_by_id(cls, device_id):
        """Fetches a device from the database by its ID.

        Args:
            device_id (str): The ID of the device to fetch.

        Returns:
            Device: The device with the specified ID, or None if not found.
        """
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        result = cursor.fetchone()
        if result:
            return Device(result[0], result[1], result[2], result[3])
        else:
            return None

    @classmethod
    def get_latest_key(cls):
        """
        Get last triggered key, to add new users by clicking on any reader
        """
        connection = sqlite3.connect("database.db")
        rows = (
            connection.cursor()
            .execute(
                "SELECT user_key "
                "FROM event_logs "
                "WHERE user_key IS NOT NULL AND operation_type = 'deny_access' "
                "ORDER BY operation_time DESC LIMIT 1"
            )
            .fetchone()
        )
        connection.close()
        if rows is None:
            return None

        return rows[0]