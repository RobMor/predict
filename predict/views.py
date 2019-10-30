import json
import sqlite3

import flask
import requests
import flask_login

from predict import app, login_manager
import predict.cve
import predict.auth
import predict.github
import predict.conflict_resolution
import predict.sqlite3_helper as sql3h
from predict.models import User
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


@app.route("/")
def base():
    # If they're logged in direct to dashboard, if not direct to login
    # stop requiring me to log in grr!!
    logged_in = True  # flask_login.current_user.is_authenticated
    if logged_in:
        return flask.redirect(flask.url_for("dashboard"))
    else:
        return flask.redirect(flask.url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # If the information is a GET, then return the form.
    if flask.request.method == "GET":
        return flask.render_template("login.html", invalidLogin = False)
    # If the information is a POST, then validate the data that is passed in
    elif flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]

        #TODO: sanitize input further?

        print(
            "Here are the currently known users when the user tried to login: "
            + str(sql3h.display_AllUsers())
        )
        current_user = sql3h.check_UserExists(username, password)
        # If valid, send the user to the dashboard
        if current_user:
            print("logging in current user " + str(current_user) + " "+ str(username))
            current_user_obj = User(username, password)
            flask_login.login_user(current_user_obj)
            return flask.redirect(
                flask.url_for("dashboard")
            )
        else:
            return flask.render_template("login.html", invalidLogin = True), 422
    else:
        flask.abort(400) #Login should only handle GET and POST requests.


@app.route("/register", methods=["GET", "POST"])
def register():
    print("register function")
    if flask.request.method == "GET":
        return flask.render_template("register.html", userExists = False, username = "")
    if flask.request.method == "POST":

        # TODO: Sanitize input further?

        username = flask.request.form["username"]
        password = flask.request.form["password"]

        if sql3h.check_UserNameExists(username):
            return flask.render_template("register.html", userExists = True, username = username)
        # Ensure there is not a user like this in the database
        else:
            sql3h.insert_User(username, password)
            return flask.redirect(flask.url_for("login"))
    else:
        error(400)


@app.route("/dashboard")
def dashboard():
    is_logged_in = True  # flask_login.current_user.is_authenticated
    if is_logged_in:
        return flask.render_template("dashboard.html")
    else:
        return flask.redirect(flask.url_for("login"))


@app.route("/resolution")
def conflict_resolution():
    # Login required:
    # if not flask_login.current_user.is_authenticated:
    #    return flask.redirect(flask.url_for("login"))

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
            "CVE-1234-5678",
            "tgiddings",
            "thisisareponame",
            "thisisarepouser",
            "3k432k4h",
            "fix_file1.cpp",
            "98018927",
            "intro_file2.cpp",
        ),
        (
            "CVE-1234-5678",
            "jbelke",
            "thisisareponame",
            "thisisarepouser",
            "3k432k4h",
            "fix_file1.cpp",
            "09sdf09sf",
            "intro_file1.cpp",
        ),
        (
            "CVE-1234-5678",
            "rmorrison",
            "thisisareponame",
            "thisisarepouser",
            "ihg6yhud",
            "fix_file2.cpp",
            "21b9de987ac",
            "intro_file1.cpp",
        ),
        (
            "CVE-1234-5678",
            "cwolff",
            "thisisareponame",
            "thisisarepouser",
            "ihg6yhud",
            "fix_file2.cpp",
            "21b9de987ac",
            "intro_file1.cpp",
        ),
        (
            "CVE-8765-4321",
            "elin",
            "thisisareponame",
            "thisisarepouser",
            "123485",
            "fix_file3.py",
            "21b9de9erwe",
            "intro_file58.fortranlol",
        ),
        (
            "CVE-8765-4321",
            "cwolff",
            "thisisareponame",
            "thisisarepouser",
            "ihg6yhud",
            "fix_file2.cpp",
            "21b9de987ac",
            "intro_file1.cpp",
        ),
        (
            "CVE-8765-4321",
            "jbelke",
            "thisisareponame",
            "thisisarepouser",
            "123485",
            "lolXD.py",
            "4206969",
            "elonmuskrat.cobal",
        ),
        (
            "CVE-867-5309",
            "thenson",
            "thisisareponame",
            "thisisarepouser",
            "ab73b9b",
            "jennyigoturnumber.onehitwonder",
            "3jd9983",
            "g**gleisabadword.purtilo",
        ),
        (
            "CVE-867-5309",
            "ckruskal",
            "isthisthekrustykrab",
            "nothisispatrick",
            "ab73b9b",
            "kruskalkrab.clyde",
            "3jd9983",
            "krabbypatty.recipe",
        ),
        (
            "CVE-867-5309",
            "mzuckerberg",
            "robotrepo",
            "robotuser",
            "7538938",
            "hellofellow.humans",
            "3jd9983",
            "notarobot.beepboop",
        ),
        (
            "CVE-867-5309",
            "MrMiyagi",
            "thisisareponame",
            "thisisarepouser",
            "7538938",
            "crane.kick",
            "3jd9983",
            "daniel.san",
        ),
        (
            "CVE-867-5309",
            "esnowden",
            "thisisareponame",
            "thisisarepouser",
            "3209dbce9",
            "turnoffyourwebcam.nsa",
            "0932840293",
            "myfbiagent.lol",
        ),
        (
            "CVE-2020-2020",
            "jbelke",
            "thisisareponame",
            "thisisarepouser",
            "123485",
            "lolXD.py",
            "4206969",
            "elonmuskrat.cobal",
        ),
        (
            "CVE-2020-2020",
            "lebronshairline",
            "thisisareponame",
            "thisisarepouser",
            "123485",
            "lolXD.py",
            "4206969",
            "elonmuskrat.cobal",
        ),
        (
            "CVE-2020-2020",
            "bgates",
            "thisisareponame",
            "thisisarepouser",
            "123485",
            "lolXD.py",
            "4206969",
            "elonmuskrat.cobal",
        )
    ]

    currentUser = "jbelke"  # TODO: Replace with flask_login.current_user.username
    blocks = predict.conflict_resolution.splitByCveId(entries)
    newBlocks = []
    for block in blocks:
        block = predict.conflict_resolution.moveUserToFront(block, currentUser)
        currUserEntry = block[0]
        for i in range(0, len(block)):
            block[i] = predict.conflict_resolution.appendURLs(block[i])
            if block[0][1] == currentUser:
                if i != 0:
                    block[i] = predict.conflict_resolution.insertAgreements(
                        block[i], currUserEntry
                        )
            else:
                block[i] = predict.conflict_resolution.insertAgreements(
                    block[i], None
                    )
        if block[0][1] == currentUser:
            block = predict.conflict_resolution.insertPercentages(block)
        if block is not None:
            newBlocks.append(block)
    return flask.render_template(
        "conflict_resolution.html", blocks=newBlocks, current_user=currentUser
    )  # TODO: Replace with get_current_user


@app.route("/cve/<cve_id>")
@flask_login.login_required
def cve_base(cve_id):
    cve_data = predict.cve.get_cve(cve_id)

    if len(cve_data.get("git_links", [])) > 0:
        return flask.redirect(cve_data["git_links"][0][1])

    return flask.render_template("cve_sidebar.html", cve_data=cve_data)


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


@app.route("/cve/<cve_id>/blame/<repo_user>/<repo_name>/<commit>/<file_name>")
def blame_page(cve_id, repo_user, repo_name, commit, file_name):
    result = predict.github.get_blame_page(
        cve_id, repo_user, repo_name, commit, file_name
    )
    cve_data = predict.cve.get_cve(cve_id)
    print(json.dumps(result, indent=4))
    return flask.render_template("blame.html", cve_data=cve_data, github_data=result)

    return "TODO"
