import json
import sqlite3

import flask
import requests

from predict import app
import predict.cve
import predict.github

# Constants for database entry indices.
# May not be accurate, update later as necessary.
# Haven't yet figured out how to use these values in templates without passing them all in
# as render_template arguments, which feels messy. May just get rid of these later, we'll see.
#CVE_ID_INDEX = 0
#USERNAME_INDEX = 1
#FIX_COMMIT_INDEX = 2
#FIX_FILE_INDEX = 3
#INTRO_COMMIT_INDEX = 4
#INTRO_FILE_INDEX = 5

@app.route("/")
def base():
    # If they're logged in direct to dashboard, if not direct to login
    logged_in = True  # TODO how to check if the user is logged in
    if logged_in:
        return flask.redirect(flask.url_for("dashboard"))
    else:
        return flask.redirect(flask.url_for("login"))


@app.route("/login")
def login():
    return flask.render_template("login.html")


@app.route("/register")
def register():
    return "TODO"


@app.route("/dashboard")
def dashboard():
    return flask.render_template("dashboard.html")


@app.route("/resolution")
def conflict_resolution():

    #try:
    #    connection = sqlite3.connect(db_file)
    #    cursor = conn.cursor()
    #    cursor.execute("SELECT cveid, username, fixcommit, fixfile, introcommit, introfile FROM <TABLE_NAME> ORDER BY cveid, username")
    #    entries = cursor.fetchall() # Get all rows
    #except Error as e:
    #    print("Connection to database failed")
    #TODO: Handle this!
    #finally:
    #    if connection:
    #        connection.close()

    #TODO: Replace this with above code!
    entries = [("1234-5678", "jbelke", "3k432k4h", "fix_file1.cpp", "09sdf09sf", "intro_file1.cpp"), ("9876-54321", "rmorrison", "ihg6yhud", "fix_file2.cpp", "21b9de987ac", "intro_file2.cpp")]
    current_user = "jbelke"
    return flask.render_template("conflict_resolution.html", entries=entries, current_user = current_user) #TODO: Replace with get_current_user


@app.route("/cve/<cve_id>")
def cve_base(cve_id):
    cve_data = predict.cve.get_cve(cve_id)

    if len(cve_data.get("github_links", [])) > 0:
        return flask.redirect(cve_data["github_links"][0][1])

    return flask.render_template("cve_sidebar.html", cve_data=cve_data)


@app.route("/cve/<cve_id>/info/<repo_user>/<repo_name>/<hash>")
def info_page(cve_id, repo_user, repo_name, hash):
    # Possibly collect these in parallel?
    cve_data = predict.cve.get_cve(cve_id)
    github_data = predict.github.get_commit(repo_user, repo_name, hash)

    return flask.render_template("commit_info.html", cve_data=cve_data, github_data=github_data)


@app.route("/cve/<cve_id>/blame/<repo_user>/<repo_name>/<hash>/<file_name>")
def blame_page(cve_id, repo_user, repo_name, hash, file_name):
    return "TODO"
