"""
Model for managing user posts
"""

from datetime import datetime
from pytz import timezone, utc

class Posts:
    def __init__(self, connection):
        self.connection = connection

    def post_exists(self, id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "select id from posts where id = %s",
                (id,)
            )
            return not cursor.fetchone() is None

    def format_post_data(self, post_data, format_date=True):
            formatted_post = {}
            formatted_post["id"] = post_data[0]
            formatted_post["username"] = post_data[1]
            formatted_post["comment"] = post_data[2]
            if format_date:
                formatted_post["date"] = self.format_date(datetime.strptime(post_data[3], "%Y-%m-%d %H:%M:%S.%f"))
            else:
                formatted_post["date"] = datetime.strptime(post_data[3], "%Y-%m-%d %H:%M:%S.%f")
            return formatted_post

    def format_date(self, date):
        def add_zero(n):
            n = str(n)
            if len(n) > 1:
                return n
            else:
                return "0%s" % n

        def am_or_pm(hour):
            if hour > 12:
                return "PM"
            else:
                return "AM"

        def hour_to_standard(hour):
            if hour > 12:
                return hour - 12
            else:
                if hour == 0:
                    return 12
                else:
                    return hour

        month_names = {
            1:"January",
            2:"February",
            3:"March",
            4:"April",
            5:"May",
            6:"June",
            7:"July",
            8:"August",
            9:"September",
            10:"October",
            11:"November",
            12:"December"
        }

        # Timezone conversions
        eastern = timezone("US/Eastern")

        utc_now = utc.localize(datetime.utcnow())
        utc_database = utc.localize(date)

        local_now = utc_now.astimezone(eastern)
        local_database = utc_database.astimezone(eastern)

        if local_now.day == local_database.day and local_now.month == local_database.month and local_now.year == local_database.year:
            return "%d:%s:%s %s" % (
                hour_to_standard(local_database.hour),
                add_zero(local_database.minute),
                add_zero(local_database.second),
                am_or_pm(local_database.hour)
            )
        elif local_now.year == local_database.year:
            return "%s %d, %d:%s %s" % (
                month_names[local_database.month],
                date.day,
                hour_to_standard(local_database.hour),
                add_zero(local_database.minute),
                am_or_pm(local_database.hour)
            )

        else:
            return "%s %d %d, %d:%s %s" % (
                month_names[local_database.month],
                local_database.day,
                local_database.year,
                hour_to_standard(local_database.hour),
                add_zero(local_database.minute),
                am_or_pm(local_database.hour)
            )

    def get_post_by_id(self, id, format_date=True):
        with self.connection.cursor() as cursor:
            if self.post_exists(id):
                cursor.execute(
                    "select * from posts where id = %s",
                    (id,)
                )
                post_data = cursor.fetchone()
                return self.format_post_data(post_data, format_date=format_date)
            else:
                return False

    def list_posts(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "select * from posts"
            )
            posts = cursor.fetchall()

            return list(map(self.format_post_data, posts))

    def list_posts_by_username(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "select * from posts where username = %s order by id desc",
                (username,)
            )
            posts = cursor.fetchall()

            #ensures that the user has posts
            if len(posts) >= 1:
                return list(map(self.format_post_data, posts))
            else:
                return None

    def new_post(self, username, comment):
        with self.connection.cursor() as cursor:
            if username and comment:
                cursor.execute(
                    "insert into posts (username, comment, date) values (%s,%s,%s)",
                    (username, comment, datetime.utcnow())
                )
                self.connection.commit()
                return True
            else:
                return False


    def delete_post_by_id(self, id):
        with self.connection.cursor() as cursor:
            if self.post_exists(id):
                cursor.execute(
                    "delete from posts where id = %s",
                    (id,)
                )
                self.connection.commit()
                return True
            else:
                return False

    def delete_posts_by_user(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "delete from posts where username = %s",
                (username,)
            )
            self.connection.commit()

    def edit_post_by_id(self, id, updated_text):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "update posts set comment = %s where id = %s",
                (updated_text, id)
            )
            self.connection.commit()
