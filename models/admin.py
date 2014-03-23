class Admin:
    def __init__(self, connection):
        self.connection = connection

    def admin_exists(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "select username from admin where username = %s",
                (username,)
            )
            return not cursor.fetchone() is None

    def new_admin(self, username):
        with self.connection.cursor() as cursor:
            if not self.admin_exists(username):
                cursor.execute(
                    "insert into admin (username) values (%s)",
                    (username,)
                )
                self.connection.commit()
                return True
            else:
                return False

    def delete_admin(self, username):
        with self.connection.cursor() as cursor:
            if self.admin_exists(username):
                cursor.execute(
                    "delete from admin where username = %s",
                    (username,)
                )
                self.connection.commit()
                return True
            else:
                return False