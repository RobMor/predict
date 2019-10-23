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
        link = data["github_links"][0]

        return flask.redirect(
            url_for(
                "info_page",
                cve_id=cve_id,
                repo_user=link["repo_user"],
                repo_name=link["repo_name"],
                hash=link["hash"],
            )
        )

    return flask.render_template("cve_sidebar.html")


@app.route("/cve/<cve_id>/info/<repo_user>/<repo_name>/<hash>")
def info_page(cve_id, repo_user, repo_name, hash):

    # TODO -- validate input here!!!

    # cve_data = CVEWebScraper(cve_id).run() # TODO -- How to save this data from the previous request!!

    # link = cve_data["links"][int(link_num)]
    # github_data = GitHubWebScraper(link).run()

    # return render_template(
    #     "commit_info.html",
    #     cve_id=cve_data["ID"],
    #     cve_desc=cve_data["desc"],
    #     cve_links=cve_data["links"],
    #     commit_hash=github_data["hash"],
    #     commit_msg=github_data["msg"],
    #     commit_files=github_data["files"],
    # )

    return "TODO"


@app.route("/cve/<cve_id>/blame/<repo_user>/<repo_name>/<hash>/<file_name>")
def blame_page(cve_id, repo_user, repo_name, hash, file_name):
    return "TODO"
