"""
This is a sample application to become familiar with Flask
"""

from flask import Flask, request, session, render_template, url_for, redirect, flash
from psycopg2 import connect
from models.users import Users
from models.posts import Posts
from models.admin import Admin
import os

app = Flask(__name__)

# Database connection provided by Heroku
# Provide your own database credentials 
connection = connect(
    host="host",
    database="database",
    user="user",
    password="password",
    port=5432
)

users = Users(connection)
posts = Posts(connection)
admin = Admin(connection)

# Application secret key
# Provide your own secret key for security
app.secret_key = "some_unique_secret_key"

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("me"))
    else:
        return redirect(url_for("login"))

@app.route("/user/new", methods=["GET", "POST"])
def new_user():
    if request.method == "GET":
        return render_template("new_user.html")
    elif request.method == "POST":
        if request.form["username"] and request.form["password"] and request.form["confirm_password"]:
            if request.form["password"] == request.form["confirm_password"]:
                if not users.user_exists(request.form["username"]):
                    users.new_user(request.form["username"], request.form["password"])
                    session["username"] = request.form["username"]
                    return redirect(url_for("me"))
                else:
                    flash("The username %s has already been taken" % request.form["username"])
                    return redirect(url_for("new_user"))
            else:
                flash("Your password confirmation did not match your password")
                return redirect(url_for("new_user"))
        else:
            flash("Please complete all fields")
            return redirect(url_for("new_user"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session.pop("username", None)
        return render_template("login.html")
    elif request.method == "POST":
        if request.form["username"] and request.form["password"] and users.user_exists(request.form["username"]) and users.match_password(request.form["username"], request.form["password"]):
            session["username"] = request.form["username"]
            return redirect(url_for("me"))
        else:
            flash("Incorrect username or password")
            return redirect(url_for("login"))

@app.route("/user/me")
def me():
    if "username" in session:
        return render_template("view_user.html", posts=posts, username=session["username"], me=True)
    else:
        return redirect(url_for("login"))

@app.route("/user/<username>")
def view_user(username):
    if "username" in session and session["username"] == username:
        return redirect(url_for("me"))
    elif users.user_exists(username):
        return render_template("view_user.html", posts=posts, username=username, me=False)
    else:
        return render_template("user_not_found.html", username=username)

@app.route("/post", methods=["GET", "POST"])
def new_post():
    if "username" in session:
        if request.method == "GET":
            return render_template("new_post.html")
        elif request.method == "POST":
            if request.form["comment"]:
                posts.new_post(session["username"], request.form["comment"])
                return redirect(url_for("me"))
            else:
                flash("Posts cannot be empty.")
                return redirect(render_template("new_post.html"))
    else:
        return redirect(url_for("login"))

@app.route("/post/<post_number>")
def view_post(post_number):
    if posts.post_exists(post_number):
        return render_template("view_post.html", post=posts.get_post_by_id(post_number))
    else:
        return render_template("post_not_found.html", id=post_number)

@app.route("/admin")
def admin_list_users():
    if "username" in session:
        if admin.admin_exists(session["username"]):
            return render_template("admin_list_users.html", users=users)
        else:
            flash("%s is not an administrator" % session["username"])
            return redirect(url_for("login"))
    else:
        flash("Log in as an administrator to access that page")
        return redirect(url_for("login"))

@app.route("/delete_user", methods=["POST"])
def delete_user():
    if users.user_exists(request.form["username"]):
        users.delete_user(request.form["username"])
        posts.delete_posts_by_user(request.form["username"])
        return redirect(url_for("admin_list_users"))

@app.route("/delete_post", methods=["POST"])
def delete_post():
    if posts.post_exists(request.form["id"]):
        posts.delete_post_by_id(request.form["id"])
        return redirect(url_for("me"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/user/list")
def list_users():
    return render_template("list_users.html", users=users)

@app.route("/search_user", methods=["POST"])
def search_user():
    if users.user_exists(request.form["username"]):
        return redirect(url_for("view_user", username=request.form["username"]))
    else:
        flash("User %s not found" % request.form["username"])
        return redirect(url_for("list_users"))

@app.route("/edit_post", methods=["POST"])
def edit_post():
    return render_template("edit_post.html", posts=posts, post_id=request.form["post_id"])

@app.route("/edit_post_in_database", methods=["POST"])
def edit_post_in_database():
    posts.edit_post_by_id(request.form["post_id"], request.form["comment"])
    return redirect(url_for("view_post", post_number=request.form["post_id"]))



#Errors
@app.errorhandler(404)
def error_404(error):
    return render_template("404.html"), 404

#Start the server
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        debug=True,
    )
