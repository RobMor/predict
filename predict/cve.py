import re
import time

import json
import flask
import requests
from bs4 import BeautifulSoup


def get_entry(cve_id):
    if is_valid_cve(cve_id):
        entry_in_database = False

        if entry_in_database:
            # Retrieve the entry from the database
            return None
        else:
            return process_entry(scrape_entry(cve_id))
    else:
        return None


def process_entry(entry):
    links = entry["links"]

    del entry["links"]

    entry["github_links"] = []
    entry["normal_links"] = []

    for link in links:
        if is_github_link(link):
            print(entry)
            entry["github_links"].append(change_github_link(entry["id"], link))
        # elif is_git_link(link):
        #     entry["github_links"].append(change_git_link(cve_id, link))
        else:
            entry["normal_links"].append(link)

    return entry


def scrape_entry(cve_id):
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


cve_pattern = re.compile("^CVE-\d{4}-\d{4,7}$")

def is_valid_cve(cve_id):
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
