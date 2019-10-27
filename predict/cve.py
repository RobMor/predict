import re
import time

import urllib
import flask
import requests
from bs4 import BeautifulSoup


def get_cve(cve_id):
    if is_valid_cve_id(cve_id):
        entry_in_database = False

        if entry_in_database:
            # TODO Retrieve the entry from the database here...
            return None
        else:
            raw_cve = scrape_cve(cve_id)
            return process_cve(raw_cve)
    else:
        return None


def scrape_cve(cve_id):
    # TODO -- We should be using the NVD
    entry = {"id": cve_id}
    url = "https://nvd.nist.gov/vuln/detail/{}".format(cve_id)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    entry["desc"] = soup.find("p", {"data-testid": "vuln-description"}).text

    links = soup.find_all("td", {"data-testid": re.compile("vuln-hyperlinks-link-\d+")})

    entry["links"] = []
    for link in links:
        entry["links"].append(link.find("a").get("href"))

    return entry


def process_cve(entry):
    links = entry["links"]

    del entry["links"]

    entry["github_links"] = []
    entry["normal_links"] = []

    for link in links:
        # TODO matching same regex twice here...
        parsed_link = urllib.parse.urlparse(link)
        if is_github_link(parsed_link):
            entry["github_links"].append((link, convert_github_link(entry["id"], parsed_link)))
        elif is_git_link(parsed_link):
            entry["github_links"].append((link, convert_git_link(entry["id"], parsed_link)))

            print(entry["github_links"][-1])
        else:
            entry["normal_links"].append(link)

    return entry


cve_pattern = re.compile("^CVE-\d{4}-\d{4,7}$")


def is_valid_cve_id(cve_id):
    return cve_pattern.match(cve_id) is not None


github_pattern = re.compile("\/?([A-Za-z0-9\-]+)\/([A-Za-z0-9\-]+)\/commit\/([0-9a-f]{5,40})\/?$")

def is_github_link(link):
    return link.netloc == "github.com" and github_pattern.match(link.path) is not None


def convert_github_link(cve_id, link):
    match = github_pattern.match(link.path)

    return flask.url_for(
        "info_page",
        cve_id=cve_id,
        repo_user=match.group(1),
        repo_name=match.group(2),
        commit=match.group(3),
    )


known_repositories = {
    "git.qemu.org": ("qemu", "qemu"),
}

def is_git_link(link):
    return link.netloc in known_repositories


def convert_git_link(cve_id, link):
    info = urllib.parse.parse_qs(link.query)
    
    repo_user, repo_name = known_repositories[link.netloc]

    commit = info["h"][0]

    return flask.url_for(
        "info_page",
        cve_id=cve_id,
        repo_user=repo_user,
        repo_name=repo_name,
        commit=commit,
    )
