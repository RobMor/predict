import json
import requests

from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from flask import redirect

from predict import app
from predict.scrapers import CVEWebScraper
from predict.scrapers import GitHubWebScraper


@app.route("/")
def cve_entry_page():
    return render_template("cve_entry.html")


@app.route("/cve/<cve_id>")
def cve_base(cve_id):

    # TODO -- Validate cve id here!

    cve_data = CVEWebScraper(cve_id).run()

    for num, link in enumerate(cve_data["links"]):
        # Display the page for the first github link we find
        if "github.com" in link:  # TODO -- More sophisticated checks in the future
            hash = link.split("/")[-1]
            return redirect(url_for("commit_info_page", cve_id=cve_id, link_num=num, hash=hash))

    # TODO -- Give more information to the template as to which links are gitub links
    return render_template(
        "cve_selected.html",
        cve_id=cve_data["ID"],
        cve_desc=cve_data["desc"],
        cve_links=cve_data["links"],
    )

@app.route("/cve/<cve_id>/<link_num>/<hash>")
def commit_info_page(cve_id, link_num, hash):

    # TODO -- validate input here!!!

    cve_data = CVEWebScraper(cve_id).run() # TODO -- Hmmmm

    link = cve_data["links"][int(link_num)]
    github_data = GitHubWebScraper(link).run()

    return render_template(
        "commit_info.html",
        cve_id=cve_data["ID"],
        cve_desc=cve_data["desc"],
        cve_links=cve_data["links"],
        commit_hash=github_data["hash"],
        commit_msg=github_data["msg"],
        commit_files=github_data["files"],
    )


# @app.route("/add_commit_page")
# def add_commit_page():
#     if request.form["commit_link"] is not None:
#         return render_template(
#             "commit_page.html",
#             context=CVEWebScraper.strip_commit_page(request.form["commit_link"]),
#         )


# @app.route("/mark_commit_as_intro")
# def mark_commit_as_intro():
#     if (
#         request.form["commit_link"] is not None
#         and request.form["cve_number"] is not None
#     ):
#         print(
#             "CVE entry {} solved at {}".format(
#                 request.form["cve_number"], request.form["commit_link"]
#             )
#         )
