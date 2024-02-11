import sqlite3
from flask import current_app as app


class User:
    def __init__(self, name, key, slack_id=None):
        self.name = name
        self.key = key
        self.slack_id = slack_id

    @classmethod
    def get_by_key(cls, key):
        connection = sqlite3.connect(app.config["DATABASE_URI"])
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE key = ?", (key,))
        result = cursor.fetchone()
        if result:
            return User(result[0], result[1], result[2])

        return None

    def save(self):
        """
        Returns number of new user added
        """
        # Connect to the database
        conn = sqlite3.connect(app.config["DATABASE_URI"])
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE key = ?", (self.key,))
        existing_user = cursor.fetchone()
        number_of_new_user = 0
        if existing_user:
            # Update existing user data
            cursor.execute(
                "UPDATE users SET name = ?, slack_id = ? WHERE key = ?",
                (self.name, self.slack_id, self.key),
            )
        else:
            # Create new user
            cursor.execute(
                "INSERT INTO users (name, key, slack_id) VALUES (?, ?, ?)",
                (self.name, self.key, self.slack_id),
            )
            number_of_new_user = 1
            conn.commit()

        # Close the connection
        conn.close()
        return number_of_new_user

    def delete(self):
        # Connect to the database
        conn = sqlite3.connect(app.config["DATABASE_URI"])
        cursor = conn.cursor()

        # Delete user from users table
        cursor.execute("DELETE FROM users WHERE key = ?", (self.key,))
        conn.commit()

        # Delete user permissions from permissions table
        cursor.execute("DELETE FROM permissions WHERE user_key = ?", (self.key,))
        conn.commit()

        # Close the connection
        conn.close()

    @classmethod
    def get_permissions(cls, user_key=None):
        # Connect to the SQLite database
        conn = sqlite3.connect(app.config["DATABASE_URI"])
        cursor = conn.cursor()

        # Fetch user data and permissions
        user_data = []
        # Filter by user_key if provided
        # Here we also add "Latest Activity" column, for reporting latest any tool/door use by user
        if user_key:
            cursor.execute(
                """
                SELECT users.name, users.key,
                       (SELECT operation_time
                        FROM event_logs
                        WHERE user_key = users.key
                        ORDER BY operation_time DESC
                        LIMIT 1) AS latest_activity
                FROM users
                WHERE users.key = ?
                """,
                (user_key,),
            )
        else:
            cursor.execute(
                """
                SELECT users.name, users.key,
                       (SELECT operation_time
                        FROM event_logs
                        WHERE user_key = users.key
                        ORDER BY operation_time DESC
                        LIMIT 1) AS latest_activity
                FROM users
                """
            )

        for row in cursor.fetchall():
            user_name = row[0]
            user_key = row[1]
            latest_activity = row[2]

            # Get device permissions for the current user
            device_permissions = []
            cursor.execute("SELECT devices.id, devices.name FROM devices")
            for result in cursor.fetchall():
                device_id = result[0]
                device_name = result[1]

                # Check if device-user pair exists in permissions table
                cursor.execute(
                    "SELECT 1 FROM permissions WHERE device_id = ? and user_key = ?",
                    (device_id, user_key),
                )
                exists_result = cursor.fetchone()

                # Set allowed flag based on existence in permissions table
                allowed = bool(exists_result is not None)  # Default to False

                # Append device information to the permissions list
                device_permissions.append(
                    {
                        "device_id": device_id,
                        "device_name": device_name,
                        "allowed": allowed,
                    }
                )

            # Combine user information and permissions into a single record
            user_record = {
                "user_name": user_name,
                "user_key": user_key,
                "permissions": device_permissions,
                "latest_activity": latest_activity,
            }
            user_data.append(user_record)

        # Close the database connection
        conn.close()

        return user_data

    def has_permission_for_device(self, device_id):
        connection = sqlite3.connect(app.config["DATABASE_URI"])
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT * FROM permissions WHERE user_key = ? AND device_id = ?
        """,
            (self.key, device_id),
        )
        result = cursor.fetchone()

        return bool(result is not None)

    def add_permission(self, device_id):
        # Connect to the database
        conn = sqlite3.connect(app.config["DATABASE_URI"])
        cursor = conn.cursor()

        # Check if device exists
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        device = cursor.fetchone()

        if not device:
            raise ValueError(f"Device with ID {device_id} does not exist")

        # Add device permission for user
        cursor.execute(
            "INSERT INTO permissions (device_id, user_key) VALUES (?, ?)",
            (device_id, self.key),
        )
        conn.commit()

        # Close the connection
        conn.close()

    def remove_permission(self, device_id):
        # Connect to the database
        conn = sqlite3.connect(app.config["DATABASE_URI"])
        cursor = conn.cursor()

        # Check if device exists
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        device = cursor.fetchone()

        if not device:
            raise ValueError(f"Device with ID {device_id} does not exist")

        # Remove device permission from user
        cursor.execute(
            "DELETE FROM permissions WHERE device_id = ? AND user_key = ?",
            (device_id, self.key),
        )
        conn.commit()

        # Close the connection
        conn.close()
