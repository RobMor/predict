import json
import sqlite3

import flask
import requests
import flask_login

import predict.cve
import predict.auth
import predict.github
import predict.conflict_resolution
import predict.models


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

    if not predict.auth.valid_username(username):
        flask.flash("Your username must be one or more alphanumeric characters! Please try again.")
        return flask.render_template("register.html")

    if not predict.auth.valid_password(password):
        flask.flash("Your password must be eight or more alphanumeric characters! Please try again.")
        return flask.render_template("register.html")

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
    confirm = flask.request.form["confirm"]

    if confirm != password:
        flask.flash("Passwords entered do not match! Please try again.")
        return flask.render_template("register.html")

    if not predict.auth.valid_username(username):
        flask.flash("Your username must be one or more alphanumeric characters! Please try again.")
        return flask.render_template("register.html")

    if not predict.auth.valid_password(password):
        flask.flash("Your password must be eight or more alphanumeric characters! Please try again.")
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
    if not flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for("main.login"))

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
    entry1 = predict.models.Label()
    entry1one = predict.models.Label()
    entry2 = predict.models.Label()
    entry21 = predict.models.Label()
    entry3 = predict.models.Label()
    entry31 = predict.models.Label()
    entry32 = predict.models.Label()
    entry4 = predict.models.Label()
    entry41 = predict.models.Label()
    entry5 = predict.models.Label()
    entry6 = predict.models.Label()
    entry7 = predict.models.Label()
    entry8 = predict.models.Label()
    entry9 = predict.models.Label()
    entry10 = predict.models.Label()
    entry11 = predict.models.Label()
    entry12 = predict.models.Label()
    entry13 = predict.models.Label()
    entry14 = predict.models.Label()
    entry15 = predict.models.Label()


    entry1.cve = "CVE-1234-5678"
    entry1.username = "tgiddings"
    entry1.repo_name = "thisisareponame"
    entry1.repo_user = "thisisarepouser"
    entry1.fix_hash = "3k432k4h"
    entry1.fix_file = "fix_file1.cpp"
    entry1.intro_hash = "09sdf09sf"
    entry1.intro_file = "intro_file2.cpp"

    entry21.cve = "CVE-1234-5678"
    entry21.username = "tgiddings"
    entry21.repo_name = "thisisareponame"
    entry21.repo_user = "thisisarepouser"
    entry21.fix_hash = "3k432k4h"
    entry21.fix_file = "fix_file2.cpp"
    entry21.intro_hash = "09sdf09sf"
    entry21.intro_file = "intro_file1.cpp"

    entry1one.cve = "CVE-1234-5678"
    entry1one.username = "jbelke"
    entry1one.repo_name = "thisisareponame"
    entry1one.repo_user = "thisisarepouser"
    entry1one.fix_hash = "12345678"
    entry1one.fix_file = "fix_file1.cpp"
    entry1one.intro_hash ="87654321"
    entry1one.intro_file = "intro_file2.cpp"

    entry2.cve = "CVE-1234-5678"
    entry2.username = "jbelke"
    entry2.repo_name = "thisisareponame"
    entry2.repo_user = "thisisarepouser"
    entry2.fix_hash = "3k432k4h"
    entry2.fix_file = "fix_file2.cpp"
    entry2.intro_hash ="09sdf09sf"
    entry2.intro_file = "intro_file1.cpp"

    entry3.cve = "CVE-1234-5678"
    entry3.username = "rmorrison"
    entry3.repo_name = "thisisareponame"
    entry3.repo_user = "thisisarepouser"
    entry3.fix_hash = "i32412342"
    entry3.fix_file = "fix_file9.cpp"
    entry3.intro_hash = "1342432"
    entry3.intro_file = "intro_file1.cpp"

    entry31.cve = "CVE-1234-5678"
    entry31.username = "rmorrison"
    entry31.repo_name = "thisisareponame"
    entry31.repo_user = "thisisarepouser"
    entry31.fix_hash = "ihg6yhud"
    entry31.fix_file = "fix_file2.cpp"
    entry31.intro_hash = "21b9de987ac"
    entry31.intro_file = "intro_file2.cpp"

    entry32.cve = "CVE-1234-5678"
    entry32.username = "rmorrison"
    entry32.repo_name = "thisisareponame"
    entry32.repo_user = "thisisarepouser"
    entry32.fix_hash = "d09efau0e"
    entry32.fix_file = "fix_file69.cpp"
    entry32.intro_hash = "123412532"
    entry32.intro_file = "intro_file3.cpp"

    entry4.cve = "CVE-1234-5678"
    entry4.username = "cwolff"
    entry4.repo_name = "thisisareponame"
    entry4.repo_user = "thisisarepouser"
    entry4.fix_hash = "345215235"
    entry4.fix_file = "fix_file5.cpp"
    entry4.intro_hash = "454325436"
    entry4.intro_file = "intro_file1.cpp"

    entry41.cve = "CVE-1234-5678"
    entry41.username = "cwolff"
    entry41.repo_name = "thisisareponame"
    entry41.repo_user = "thisisarepouser"
    entry41.fix_hash = "ihg6yhud"
    entry41.fix_file = "fix_file2.cpp"
    entry41.intro_hash = "21b9de987ac"
    entry41.intro_file = "intro_file2.cpp"

    entry5.cve = "CVE-8765-4321"
    entry5.username = "elin"
    entry5.repo_name = "thisisareponame"
    entry5.repo_user = "thisisarepouser"
    entry5.fix_hash = "123485"
    entry5.fix_file = "fix_file3.py"
    entry5.intro_hash = "21b9de9erwe"
    entry5.intro_file = "intro_file58.fortranlol"
    entry6.cve = "CVE-8765-4321"
    entry6.username = "cwolff"
    entry6.repo_name = "thisisareponame"
    entry6.repo_user = "thisisarepouser"
    entry6.fix_hash = "ihg6yhud"
    entry6.fix_file = "fix_file2.cpp"
    entry6.intro_hash = "21b9de987ac"
    entry6.intro_file = "intro_file1.cpp"

    entry7.cve = "CVE-8765-4321"
    entry7.username = "jbelke"
    entry7.repo_name = "thisisareponame"
    entry7.repo_user = "thisisarepouser"
    entry7.fix_hash = "123485"
    entry7.fix_file = "lolXD.py"
    entry7.intro_hash = "4206969"
    entry7.intro_file = "elonmuskrat.cobal"

    entry8.cve = "CVE-867-5309"
    entry8.username = "thenson"
    entry8.repo_name = "thisisareponame"
    entry8.repo_user = "thisisarepouser"
    entry8.fix_hash = "ab73b9b"
    entry8.fix_file = "jennyigoturnumber.onehitwonder"
    entry8.intro_hash = "3jd9983"
    entry8.intro_file = "g**gleisabadword.purtilo"

    entry9.cve = "CVE-867-5309"
    entry9.username = "ckruskal"
    entry9.repo_name = "isthisthekrustykrab"
    entry9.repo_user = "nothisispatrick"
    entry9.fix_hash = "ab73b9b"
    entry9.fix_file = "kruskalkrab.clyde"
    entry9.intro_hash = "3jd9983"
    entry9.intro_file = "krabbypatty.recipe"

    entry10.cve = "CVE-867-5309"
    entry10.username = "mzuckerberg"
    entry10.repo_name = "robotrepo"
    entry10.repo_user = "robotuser"
    entry10.fix_hash = "7538938"
    entry10.fix_file = "hellofellow.humans"
    entry10.intro_hash = "3jd9983"
    entry10.intro_file = "notarobot.beepboop"

    entry11.cve = "CVE-867-5309"
    entry11.username = "MrMiyagi"
    entry11.repo_name = "thisisareponame"
    entry11.repo_user = "thisisarepouser"
    entry11.fix_hash = "7538938"
    entry11.fix_file = "crane.kick"
    entry11.intro_hash = "3jd9983"
    entry11.intro_file = "daniel.san"

    entry12.cve = "CVE-867-5309"
    entry12.username = "esnowden"
    entry12.repo_name = "thisisareponame"
    entry12.repo_user = "thisisarepouser"
    entry12.fix_hash = "3209dbce9"
    entry12.fix_file = "turnoffyourwebcam.nsa"
    entry12.intro_hash = "0932840293"
    entry12.intro_file = "myfbiagent.lol"

    entry13.cve = "CVE-2020-2020"
    entry13.username = "jbelke"
    entry13.repo_name = "thisisareponame"
    entry13.repo_user = "thisisarepouser"
    entry13.fix_hash = "123485"
    entry13.fix_file = "lolXD.py"
    entry13.intro_hash = "4206969"
    entry13.intro_file = "elonmuskrat.cobal"

    entry14.cve = "CVE-2020-2020"
    entry14.username = "lebronshairline"
    entry14.repo_name = "thisisareponame"
    entry14.repo_user = "thisisarepouser"
    entry14.fix_hash = "123485"
    entry14.fix_file = "lolXD.py"
    entry14.intro_hash = "4206969"
    entry14.intro_file = "elonmuskrat.cobal"

    entry15.cve = "CVE-2020-2020"
    entry15.username = "bgates"
    entry15.repo_name = "thisisareponame"
    entry15.repo_user = "thisisarepouser"
    entry15.fix_hash = "123485"
    entry15.fix_file = "lolXD.py"
    entry15.intro_hash = "4206969"
    entry15.intro_file = "elonmuskrat.cobal"

    entries = [entry1, entry21, entry1one, entry2, entry3, entry31, entry32, entry4, entry41, entry5, entry6, entry7, entry8,
        entry9, entry10, entry11, entry12, entry13, entry14, entry15]

    currentUser = "jbelke"  # TODO: Replace with flask_login.current_user.get_id()
    blocks = predict.conflict_resolution.processEntries(entries, currentUser);
#    blocks = predict.conflict_resolution.splitByCveId(entries)
#    newBlocks = []
#    for block in blocks:
#        block = predict.conflict_resolution.moveUserToFront(block, currentUser)
#        currUserEntry = block[0]
#        for i in range(0, len(block)):
#            block[i] = predict.conflict_resolution.appendURLs(block[i])
#            if block[0][1] == currentUser:
#                if i != 0:
#                    block[i] = predict.conflict_resolution.insertAgreements(
#                        block[i], currUserEntry
#                    )
#            else:
#                block[i] = predict.conflict_resolution.insertAgreements(block[i], None)
#        if block[0][1] == currentUser:
#            block = predict.conflict_resolution.insertPercentages(block)
#        if block is not None:
#            newBlocks.append(block)

    return flask.render_template(
        "conflict_resolution.html", blocks=blocks, current_user=currentUser
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
