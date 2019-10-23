from bs4 import BeautifulSoup
import requests
import json
import time

def get_entry(cve_id):
    entry_in_database = False

    if entry_in_database:
        # Retrieve the entry from the database
        return None
    else:
        return scrape_entry(cve_id)


def scrape_entry(cve_id):
    # TODO validate cve_id here!
    # TODO -- We should be using the NVD
    data = {"ID": cve_id}
    url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(
        cve_id
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