from bs4 import BeautifulSoup
import requests
import json
import time


def get_commit(repo_user, repo_name, hash):
    data = {}

    link = f"https://github.com/{repo_user}/{repo_name}/commit/{hash}"

    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    data["hash"] = hash
    data["msg"] = soup.find("div", {"class": "commit-desc"}).text

    file_headers = soup.find_all(
        "div",
        {
            "class": "file-header d-flex flex-items-center file-header--expandable js-file-header"
        },
    )

    data["files"] = []
    # print file_headers
    for file_header in file_headers:
        file_name = (
            file_header.find("div", {"class": "file-info flex-auto"})
            .find("a", {"class": "link-gray-dark"})
            .text
        )
        try:
            file_link_div = file_header.find("div", {"class": "file-actions pt-0"})
            if file_link_div is not None:
                file_link = "http://github.com{}".format(
                    file_link_div.find("a").get("href")
                )
                blame_link = file_link.replace("blob", "blame")
                history_link = file_link.replace("blob", "commits")

                data["files"].append(
                    {
                        "file_name": file_name,
                        "file_link": file_link,
                        "blame_link": blame_link,
                        "history_link": history_link,
                    }
                )
        except Exception as file_header_exc:
            print(file_header_exc)

    return data


def get_blame(repo_user, repo_name, hash, file_name):
    # TODO 
    pass