from bs4 import BeautifulSoup
import requests
import json
import time


class CVEWebScraper:

    def __init__(self, cve_number):
        self.description = ""
        self.github_commit_links = []
        self.cve_links = []
        self.time_started = None
        self.cve_page_link = ""
        self.cve_number = cve_number
        self.time_started = time.time()


    def retrieve_cve_page(self):
        request = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(self.cve_number)
        self.cve_page_link = request
        response = BeautifulSoup(requests.get(request).text, "html.parser")
        github_links = []
        cve_table = response.find("div", {"id":"GeneratedTable"})
        #print cve_table.prettify()

        self.description = cve_table.find("td", {"colspan": "2"}).text
        reference_links = cve_table.find("ul")
        for list_element in reference_links.find_all("li"):
            try:
                if list_element.find("a", recursive = False) is not None and list_element.find("a", recursive = False).get("href") is not None:
                    print list_element
                    self.cve_links.append(list_element.find("a").get("href"))
                    if "github.com" in list_element.find("a").get("href"):
                        github_links.append(list_element.find("a").get("href"))
            except Exception as e:
                print e
        self.github_commit_links = github_links
        self.cve_links = list(set(self.cve_links))

    def retrieve_git_blame(self):
        data = {}
        x = 0
        for github_commit_link in self.github_commit_links:
            data[github_commit_link] = {
                "commit_description": "",
                "files":[],
                "generated_id": "commit_{}".format(x)
            }
            response = BeautifulSoup(requests.get(github_commit_link).text, "html.parser")
            data[github_commit_link]["commit_description"] = response.find("div", {"class":"commit-desc"}).text
            file_headers = response.find_all(
                "div", {"class":"file-header d-flex flex-items-center file-header--expandable js-file-header"}
            )
            #print file_headers
            for file_i in file_headers:
                file_description = file_i.find("div", {"class":"file-info flex-auto"}).find("a", {"class":"link-gray-dark"}).text
                try:
                    file_link_div = file_i.find("div", {"class":"file-actions pt-0"})
                    if file_link_div is not None:
                        file_link = "https://github.com{}".format(file_link_div.find("a").get("href"))
                        blame_file_link = file_link.replace("blob", "blame")
                        history_file_link = file_link.replace("blob", "commits")
                        data[github_commit_link]["files"].append(
                            {
                                "file_name": file_description,
                                "file_link": file_link,
                                "git_blame_link": blame_file_link,
                                "git_history_link": history_file_link
                            }
                        )
                except Exception as file_header_exc:
                    print file_header_exc
            x= x+1
        return data

    @staticmethod
    def strip_commit_page(github_commit_link, id):
        data = {}
        data[github_commit_link] = {
            "commit_description": "",
            "files": [],
            "generated_id": "commit_{}".format(id)
        }
        response = BeautifulSoup(requests.get(github_commit_link).text, "html.parser")
        data[github_commit_link]["commit_description"] = response.find("div", {"class": "commit-desc"}).text
        file_headers = response.find_all(
            "div", {"class": "file-header d-flex flex-items-center file-header--expandable js-file-header"}
        )
        # print file_headers
        for file_i in file_headers:
            file_description = file_i.find("div", {"class": "file-info flex-auto"}).find("a", {
                "class": "link-gray-dark"}).text
            try:
                file_link_div = file_i.find("div", {"class": "file-actions pt-0"})
                if file_link_div is not None:
                    file_link = "http://github.com{}".format(file_link_div.find("a").get("href"))
                    blame_file_link = file_link.replace("blob", "blame")
                    history_file_link = file_link.replace("blob", "commits")
                    data[github_commit_link]["files"].append(
                        {
                            "file_name": file_description,
                            "file_link": file_link,
                            "git_blame_link": blame_file_link,
                            "git_history_link": history_file_link
                        }
                    )
            except Exception as file_header_exc:
                print file_header_exc
        return data


    def run_scraper(self):
        self.retrieve_cve_page()
        end_data ={}
        end_data["commit_entries"] = self.retrieve_git_blame()
        end_data["cve_description"] = self.description
        end_data["time_taken"] = time.time()-self.time_started
        return end_data

if __name__ == "__main__":
    scraper = CVEWebScraper("CVE-2014-4014")
    scraper.retrieve_cve_page()
    print "\n".join(["{}".format(link) for link in scraper.github_commit_links])
    data_recovered = scraper.retrieve_git_blame()
    print "Completed in: {}".format(time.time()-scraper.time_started)
    print json.dumps(data_recovered, indent=4)
