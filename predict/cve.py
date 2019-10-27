import re
import time

import json
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
    url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"

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
        if is_github_link(link):
            entry["github_links"].append(change_github_link(entry["id"], link))
        # elif is_git_link(link):
        #     entry["github_links"].append(change_git_link(cve_id, link))
        else:
            entry["normal_links"].append(link)

    return entry


cve_pattern = re.compile("^CVE-\d{4}-\d{4,7}$")

def is_valid_cve_id(cve_id):
    return cve_pattern.match(cve_id) is not None


github_pattern = re.compile("^(https?:\/\/)?(www\.)?github\.com\/([A-Za-z0-9\-]+)\/([A-Za-z0-9\-]+)\/commit\/([0-9a-f]{5,40})\/?$")

def is_github_link(link):
    return github_pattern.match(link) is not None


# git_pattern = re.compile("^(https?:\/\/)?(www\.)?(git\.[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}).*$") # TODO messy

# def is_git_link(link):
#     return git_pattern.match(link) is not None


def change_github_link(cve_id, link):
    match = github_pattern.match(link)

    return link, flask.url_for(
        "info_page",
        cve_id=cve_id,
        repo_user=match.group(3),
        repo_name=match.group(4),
        hash=match.group(5)
    )


# known_github_repositories = {
#     "git.qemu.org": "github.com/qemu/qemu",
#     "git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git": "github.com/torvalds/linux",
# }

# def change_git_link(cve_id, link):
#     match = git_pattern.match(link)

#     repo_url = match.group(2)

#     if repo_url in known_github_repositories:
#         repo_user, repo_name = known_github_repositories[repo_url]
#     else:
#         # TODO what to do in this case...
#         raise ValueError("Link is not a known github repository")
