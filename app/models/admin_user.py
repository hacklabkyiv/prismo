import sqlite3

import argon2
from flask_login import UserMixin
from flask import current_app as app

class AdminUser(UserMixin):
    def __init__(self, username, password=None):
        self.username = username
        if password:
            self.hashed_password = argon2.PasswordHasher().hash(password)
        self.id = 1

    def check_password(self, password):
        connection = sqlite3.connect(app.config["DATABASE_URI"])
        cursor = connection.cursor()

        cursor.execute("SELECT password FROM admins WHERE username = ?", (self.username,))
        result = cursor.fetchone()
        connection.close()
        if not result:
            app.logger.warning(f"Username not found")
            return False
        try:
            app.logger.info(f"Verify hash result:", argon2.PasswordHasher().verify(result[0], password))
            return True
        except argon2.exceptions.VerifyMismatchError:
            app.logger.warning("Wrong password")
            return False

    def create_user(self):
        connection = sqlite3.connect(app.config["DATABASE_URI"])
        cursor = connection.cursor()
        cursor.execute("INSERT OR REPLACE INTO admins (id, username, password) VALUES (1, ?, ?)",
                       (self.username, self.hashed_password))
        connection.commit()
        connection.close()

    def is_authenticated(self):
        return True
