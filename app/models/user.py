#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 00:59:01 2023

@author: artsin
"""
import sqlite3


class User:
    def __init__(self, name, key, slack_id):
        self.name = name
        self.key = key
        self.slack_id = slack_id

    @classmethod
    def create_table(cls):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                name TEXT NOT NULL,
                key TEXT NOT NULL UNIQUE,
                slack_id TEXT DEFAULT NULL
            )
        """
        )
        connection.commit()
        connection.close()

    def save(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO users (name, key, slack_id)
            VALUES (?, ?, ?)
        """,
            (self.name, self.key, self.slack_id),
        )
        connection.commit()
        connection.close()

    @classmethod
    def get_by_key(cls, key):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE key = ?", (key,))
        result = cursor.fetchone()
        if result:
            return User(result[0], result[1], result[2])
        else:
            return None

    @classmethod
    def get_permissions(cls):
        # Connect to the SQLite database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Fetch user data and permissions
        user_data = []
        cursor.execute("SELECT users.name, users.key FROM users")
        for row in cursor.fetchall():
            user_name = row[0]
            user_key = row[1]

            # Get device permissions for the current user
            device_permissions = []
            cursor.execute("SELECT devices.id, devices.name FROM devices")
            for row in cursor.fetchall():
                device_id = row[0]
                device_name = row[1]

                # Check if device-user pair exists in permissions table
                cursor.execute(
                    "SELECT 1 FROM permissions WHERE device_id = ? and user_key = ?",
                    (device_id, user_key),
                )
                exists_result = cursor.fetchone()

                # Set allowed flag based on existence in permissions table
                if exists_result:
                    allowed = True  # Explicit permission found
                else:
                    allowed = False  # No explicit permission found

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
            }
            user_data.append(user_record)

        # Close the database connection
        conn.close()

        return user_data

    def has_permission_for_device(self, device_id):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT * FROM permissions WHERE user_key = ? AND device_id = ?
        """,
            (self.key, device_id),
        )
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False

    def add_permission_for_device(self, device_id):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO permissions (user_key, device_id)
            VALUES (?, ?)
        """,
            (self.key, device_id),
        )
        connection.commit()
        connection.close()

    def remove_permission_for_device(self, device_id):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM permissions WHERE user_key = ? AND device_id = ?",
            (self.key, device_id),
        )
        connection.commit()
        connection.close()


x = User.get_permissions()
print(x)
