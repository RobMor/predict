import json
import sqlite3

import flask
import requests
import flask_login

import predict.cve
import predict.auth
import predict.github
import predict.conflict_resolution


blueprint = flask.Blueprint("main", __name__)


@blueprint.route("/")
@flask_login.login_required
def base():
    return flask.redirect(flask.url_for("main.dashboard"))


@blueprint.route("/login", methods=["GET"])
def login():
    return flask.render_template("login.html", invalidLogin=False)


@blueprint.route("/login", methods=["POST"])
def login_post():
    username = flask.request.form["username"]
    password = flask.request.form["password"]

    if not predict.auth.is_valid_user(username, password):
        flask.flash("Invalid login credentials!")
        return flask.render_template("login.html")

    authorized = predict.auth.authenticate_user(username, password)

    # If valid send the user to the dashboard
    if authorized:
        return flask.redirect(flask.request.args.get("next", flask.url_for("main.dashboard")))
    else:
        flask.flash("Unrecognized credentials! Please try again.")
        return flask.render_template("login.html")


@blueprint.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()

    return flask.redirect(flask.url_for("main.base"))


@blueprint.route("/register", methods=["GET"])
def register():
    return flask.render_template("register.html")


@blueprint.route("/register", methods=["POST"])
def register_post():
    username = flask.request.form["username"]
    password = flask.request.form["password"]

    if not predict.auth.is_valid_user(username, password):
        flask.flash("Invalid registration credentials!")
        return flask.render_template("register.html")

    created = predict.auth.create_user(username, password)

    if created:
        return flask.redirect(flask.url_for("main.login"))
    else:
        flask.flash("That username already exists! Please try again.")
        return flask.render_template("register.html")


@blueprint.route("/dashboard")
@flask_login.login_required
def dashboard():
    return flask.render_template("dashboard.html")


@blueprint.route("/resolution")
@flask_login.login_required
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
        ),
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
                block[i] = predict.conflict_resolution.insertAgreements(block[i], None)
        if block[0][1] == currentUser:
            block = predict.conflict_resolution.insertPercentages(block)
        if block is not None:
            newBlocks.append(block)
    return flask.render_template(
        "conflict_resolution.html", blocks=newBlocks, current_user=currentUser
    )  # TODO: Replace with get_current_user


@blueprint.route("/cve/<cve_id>")
@flask_login.login_required
def cve_base(cve_id):
    cve_data = predict.cve.get_cve(cve_id)

    if len(cve_data.get("git_links", [])) > 0:
        return flask.redirect(cve_data["git_links"][0][1])

    return flask.render_template("cve_sidebar.html", cve_data=cve_data)


@blueprint.route("/cve/<cve_id>/info/<repo_user>/<repo_name>/<commit>")
@flask_login.login_required
def info_page(cve_id, repo_user, repo_name, commit):
    cve_data = predict.cve.get_cve(cve_id)
    github_data = predict.github.retrieve_commit_page(
        cve_id, repo_user, repo_name, commit
    )

    return flask.render_template(
        "commit_info.html", cve_data=cve_data, github_data=github_data
    )


@blueprint.route("/cve/<cve_id>/blame/<repo_user>/<repo_name>/<commit>/<path:file_name>")
@flask_login.login_required
def blame_page(cve_id, repo_user, repo_name, commit, file_name):
    cve_data = predict.cve.get_cve(cve_id)
    result = predict.github.get_blame_page(
        cve_id, repo_user, repo_name, commit, file_name
    )

    return flask.render_template("blame.html", cve_data=cve_data, github_data=result)


@blueprint.errorhandler(404)
def page_not_found(e):
    return flask.render_template("error.html", error=e)
