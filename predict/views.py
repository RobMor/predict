import json
import sqlite3

import flask
import requests
import flask_login

from predict import app
import predict.cve
import predict.github
from predict.user import User

# Constants for database entry indices.
# May not be accurate, update later as necessary.
# Haven't yet figured out how to use these values in templates without passing them all in
# as render_template arguments, which feels messy. May just get rid of these later, we'll see.
# CVE_ID_INDEX = 0
# USERNAME_INDEX = 1
# FIX_COMMIT_INDEX = 2
# FIX_FILE_INDEX = 3
# INTRO_COMMIT_INDEX = 4
# INTRO_FILE_INDEX = 5

# login stuff
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
# login config
app.config.update(SECRET_KEY="secret_xxx")
# TODO: Later on this hash of authenticated users will be converted into database calls.
users = {}
# end login stuff


@app.route("/")
def base():
    # If they're logged in direct to dashboard, if not direct to login
    logged_in = (
        flask_login.current_user.is_authenticated
    )  # TODO how to check if the user is logged in
    if logged_in:
        return flask.redirect(flask.url_for("dashboard"))
    else:
        return flask.redirect(flask.url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # If the information is a GET, then return the form.
    if flask.request.method == "GET":
        return flask.render_template("login.html")
    elif flask.request.method == "POST":
        print("hello login page post.")

        valid = False
        username = flask.request.form["username"]
        password = flask.request.form["password"]

        print("username: " + username)
        print("password: " + password)

        user = User(username, password)

        # TODO: Validate by checking the database, for now, just checking to see that user is "foo" and passwoord is "bar"
        # should suffice. Integration with Edward's login functionality.
        if username == "foo" and password == "bar":
            valid = True
            print("Valid username and password combo!")
            if username not in users:
                users[username] = user

        if valid:
            flask_login.login_user(user)
            return flask.redirect(
                flask.url_for("dashboard")
            )  # If valid, send the user to the dashboard
        else:
            # TODO: Return an appended version of the login page asking to try again, and should
            # probably wipe the form data as well.
            return "Invalid login! Please try again! (In the future this should get appended to the login page.)"

        # If the information is a POST, then validate the data that is passed in
    else:
        print("wrong kind of request got routed here somehow.")


@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "GET":
        return flask.render_template("register.html")
    if flask.request.method == "POST":
        return "Submitted the registration form."


@flask_login.login_required  # TODO: Figure out why this annotation is not preventing access
@app.route("/dashboard")
def dashboard():
    if flask_login.current_user.is_authenticated:
        return flask.render_template("dashboard.html")
    else:
        return flask.redirect(flask.url_for("login"))


@flask_login.login_required
@app.route("/resolution")
def conflict_resolution():

    # try:
    #    connection = sqlite3.connect(db_file)
    #    cursor = conn.cursor()
    #    cursor.execute("SELECT cveid, username, fixcommit, fixfile, introcommit, introfile FROM <TABLE_NAME> ORDER BY cveid, username")
    #    entries = cursor.fetchall() # Get all rows
    # except Error as e:
    #    print("Connection to database failed")
    # TODO: Handle this!
    # finally:
    #    if connection:
    #        connection.close()

    # TODO: Replace this with above code!
    entries = [
        (
            "1234-5678",
            "jbelke",
            "3k432k4h",
            "fix_file1.cpp",
            "09sdf09sf",
            "intro_file1.cpp",
        ),
        (
            "9876-54321",
            "rmorrison",
            "ihg6yhud",
            "fix_file2.cpp",
            "21b9de987ac",
            "intro_file2.cpp",
        ),
    ]
    current_user = "jbelke"
    return flask.render_template(
        "conflict_resolution.html", entries=entries, current_user=current_user
    )  # TODO: Replace with get_current_user


@app.route("/cve/<cve_id>")
def cve_base(cve_id):
    cve_data = predict.cve.get_cve(cve_id)

    if len(cve_data.get("git_links", [])) > 0:
        return flask.redirect(cve_data["git_links"][0][1])

    return flask.render_template("cve_sidebar.html", cve_data=cve_data)


@flask_login.login_required
@app.route("/cve/<cve_id>/info/<repo_user>/<repo_name>/<commit>")
def info_page(cve_id, repo_user, repo_name, commit):
    # Possibly collect these in parallel?
    cve_data = predict.cve.get_cve(cve_id)
    github_data = predict.github.retrieve_commit_page(
        cve_id, repo_user, repo_name, commit
    )
    print(json.dumps(github_data, indent=4))
    return flask.render_template(
        "commit_info.html", cve_data=cve_data, github_data=github_data
    )


@flask_login.login_required
@app.route("/cve/<cve_id>/blame/<repo_user>/<repo_name>/<commit>/<file_name>")
def blame_page(cve_id, repo_user, repo_name, commit, file_name):
    result = predict.github.get_blame_page(
        cve_id, repo_user, repo_name, commit, file_name
    )
    cve_data = predict.cve.get_cve(cve_id)
    print(json.dumps(result, indent=4))
    return flask.render_template("blame.html", cve_data=cve_data, github_data=result)

    return "TODO"


"""User callback function for getting the current user.  "This callback is used to reload the user object from the 
user ID stored in the session. Called whenever a user has logged in." Authentication function."""


@login_manager.user_loader
def load_user(username):
    print("callback called with " + username)
    if username in users:
        print("found!")
        return users[username]
    else:
        print("not found.")
        return None


@app.route("/logout")
# @flask_login.login_required
def logout():
    print("logout function called!")
    if flask_login.current_user.is_authenticated:
        flask_login.logout_user()
        return flask.redirect(flask.url_for("login"))
    else:
        return "The user tried to logout when there was no user! (This should be a webpage or an error code.)"
