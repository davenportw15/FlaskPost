"""
Model for user management
"""

from hashlib import md5

class Users:
    def __init__(self, connection):
        self.connection = connection

    def user_exists(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "select username from users where username = %s",
                (username,)
            )
            return (cursor.fetchone() is not None)

    def match_password(self, username, password):
        with self.connection.cursor() as cursor:
            if self.user_exists(username):
                cursor.execute(
                    "select password from users where username = %s",
                    (username,)
                )
                return self.encrypt(password) == cursor.fetchone()[0]
            else:
                return False

    def encrypt(self, password):
        _hex = md5()
        _hex.update(password.encode("utf-8"))
        return _hex.hexdigest()

    def new_user(self, username, password):
        with self.connection.cursor() as cursor:
            if not self.user_exists(username):
                cursor.execute(
                    "insert into users (username, password) values (%s, %s)",
                    (username, self.encrypt(password))
                )
                self.connection.commit()
                return True
            else:
                return False

    def delete_user(self, username):
        with self.connection.cursor() as cursor:
            if self.user_exists(username):
                cursor.execute(
                    "delete from users where username = %s",
                    (username,)
                )
                self.connection.commit()
                return True
            else:
                return False

    def list_users(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select username from users")
            return [x[0] for x in cursor.fetchall()]