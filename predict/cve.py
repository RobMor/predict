import time

import json
import flask
import requests
from bs4 import BeautifulSoup


def get_entry(cve_id):
    # TODO validate cve_id here!

    entry_in_database = False

    if entry_in_database:
        # Retrieve the entry from the database
        return None
    else:
        return scrape_entry(cve_id)


def scrape_entry(cve_id):
    cve_data = scrape_raw_entry(cve_id)

    links = cve_data["links"]

    del cve_data["links"]

    cve_data["github_links"] = []
    cve_data["normal_links"] = []

    for link in links:
        if is_github_link(link):
            cve_data["github_links"].append(change_github_link(cve_id, link))
        else:
            cve_data["normal_links"].append(link)

    return cve_data


def scrape_raw_entry(cve_id):
    # TODO -- We should be using the NVD
    data = {"id": cve_id}
    url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(cve_id)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    cve_table = soup.find("div", {"id": "GeneratedTable"})
    # print cve_table.prettify()

    data["desc"] = cve_table.find("td", {"colspan": "2"}).text
    data["links"] = []
    for list_element in cve_table.find("ul").find_all("li"):
        try:
            if (
                list_element.find("a", recursive=False) is not None
                and list_element.find("a", recursive=False).get("href") is not None
            ):
                data["links"].append(list_element.find("a").get("href"))
        except Exception as e:
            print(e)

    return data


def is_github_link(link):
    # TODO more sophisticated verification

    return "github" in link


def change_github_link(cve_id, link):
    link = link.split("/")

    return link, flask.url_for(
        "info_page",
        cve_id=cve_id,
        repo_user=link[-4],
        repo_name=link[-3],
        hash=link[-1],
    )

