from bs4 import BeautifulSoup
import requests
import json
import time


class CVEWebScraper:
    def __init__(self, cve_id):
        self.cve_id = cve_id

    # def retrieve_git_blame(self):
    #     data = {}
    #     x = 0
    #     for github_commit_link in self.github_commit_links:
    #         data[github_commit_link] = {
    #             "commit_description": "",
    #             "files": [],
    #             "generated_id": "commit_{}".format(x),
    #         }
    #         response = BeautifulSoup(
    #             requests.get(github_commit_link).text, "html.parser"
    #         )
    #         data[github_commit_link]["commit_description"] = response.find(
    #             "div", {"class": "commit-desc"}
    #         ).text
    #         file_headers = response.find_all(
    #             "div",
    #             {
    #                 "class": "file-header d-flex flex-items-center file-header--expandable js-file-header"
    #             },
    #         )
    #         # print file_headers
    #         for file_i in file_headers:
    #             file_description = (
    #                 file_i.find("div", {"class": "file-info flex-auto"})
    #                 .find("a", {"class": "link-gray-dark"})
    #                 .text
    #             )
    #             try:
    #                 file_link_div = file_i.find("div", {"class": "file-actions pt-0"})
    #                 if file_link_div is not None:
    #                     file_link = "https://github.com{}".format(
    #                         file_link_div.find("a").get("href")
    #                     )
    #                     blame_file_link = file_link.replace("blob", "blame")
    #                     history_file_link = file_link.replace("blob", "commits")
    #                     data[github_commit_link]["files"].append(
    #                         {
    #                             "file_name": file_description,
    #                             "file_link": file_link,
    #                             "git_blame_link": blame_file_link,
    #                             "git_history_link": history_file_link,
    #                         }
    #                     )
    #             except Exception as file_header_exc:
    #                 print(file_header_exc)
    #         x = x + 1
        # return data

    def run(self):
        # TODO -- We should be using the NVD
        data = {"ID": self.cve_id}
        url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(
            self.cve_id
        )
        
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


class GitHubWebScraper:
    def __init__(self, link):
        self.link = link

    def run(self):
        data = {}

        response = requests.get(self.link)
        soup = BeautifulSoup(response.text, "html.parser")

        data["hash"] = self.link.split("/")[-1]
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
