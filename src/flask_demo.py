from flask import Flask
from flask import render_template
from flask import request

from demo import CVEWebScraper
from selenium import webdriver

import requests
import json
app = Flask(__name__)

@app.route("/")
def hello_page():
    return "Hello World"

@app.route("/template")
def template_route():
    return render_template("base_template.html")

@app.route("/cve_entry", methods=["POST"])
def recieve_cve_entry():
    if request.form["cve_entry"] is not None:
        scraper = CVEWebScraper(request.form["cve_entry"])
        data = scraper.run_scraper()
        return render_template("cve_entry_page.html", context={
            "cve_number": scraper.cve_number,
            "cve_description": scraper.description,
            "cve_links": scraper.cve_links,
            "data": data,
            "cve_page_link":scraper.cve_page_link
        })
        #return json.dumps(data, indent=4)

@app.route("/add_commit_page")
def add_commit_page():
    if request.form["commit_link"] is not None:
        return render_template("commit_page.html", context=CVEWebScraper.strip_commit_page(request.form["commit_link"]))

@app.route("/mark_commit_as_intro")
def mark_commit_as_intro():
    if request.form["commit_link"] is not None and request.form["cve_number"] is not None:
        print "CVE entry {} solved at {}".format(request.form["cve_number"], request.form["commit_link"])

@app.route("/open_selenium/<link>")
def create_selenium_page(link):
    driver = webdriver.Chrome("C:\Users\Nate\PycharmProjects\predict_demo\src\chromedriver_win32.exe")
    driver.get(link.replace("<>", "/").replace("'", ""))
    input = raw_input("Enter quit to close window")
    while input != "quit":
        raw_input("Enter quit to close window")
    driver.quit()


if __name__ == "__main__":
    app.debug= False
    app.run(host='0.0.0.0')