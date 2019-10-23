import json
import sqlite3

import flask
import requests

from predict import app
import predict.cve
import predict.github


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
    return "TODO"


@app.route("/cve/<cve_id>")
def cve_base(cve_id):
    cve_data = predict.cve.get_entry(cve_id)

    if len(cve_data.get("github_links", [])) > 0:
        return flask.redirect(cve_data["github_links"][0][1])

    return flask.render_template("cve_sidebar.html", cve_data=cve_data)


@app.route("/cve/<cve_id>/info/<repo_user>/<repo_name>/<hash>")
def info_page(cve_id, repo_user, repo_name, hash):
    # Possibly collect these in parallel?
    cve_data = predict.cve.get_entry(cve_id)
    github_data = predict.github.get_commit(repo_user, repo_name, hash)

    return flask.render_template("commit_info.html", cve_data=cve_data, github_data=github_data)


@app.route("/cve/<cve_id>/blame/<repo_user>/<repo_name>/<hash>/<file_name>")
def blame_page(cve_id, repo_user, repo_name, hash, file_name):
    return "TODO"
