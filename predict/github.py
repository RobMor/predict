
from bs4 import BeautifulSoup
import requests
import json
import re


def retrieve_commit_page(github_commit_link):

    # Initialize variables
    master_dictionary = {
        "user_name": "",
        "repository_name": "",
        "commit_hash": "",
        "commit_description": "",
        "commit_title": "",
        "author_names": [],
        "datetime": "",
        "files": {},
        "parent_commit_hashes": [],
        "page_html": ""
    }  # Create a dictionary that we will return, containing the important information on the page

    request = requests.get(github_commit_link)  # Retrieve the page from github corresponding to the link provided
    page_html = BeautifulSoup(request.text, "html.parser")  # Get a manipulable representation of the page HTML with bs4
    master_dictionary["page_html"] = page_html.prettify()  # Preserve the html page, just in case

    # Debugging output, can be removed
    #print page_html.prettify()

    # Find user name and repository name. This is located at the top of the page, near a book icon, with 2 hyperlinks
    # representing the user and repository

    author_header = page_html.find("h1", {"class": "public"})  # Find the author header on the page
    master_dictionary["user_name"] = author_header.find("span", {"class": "author"}).text  # Get the repository's author's name
    master_dictionary["repository_name"] = author_header.find("strong", {"itemprop": "name"}).text  # Get the repository's name

    # To improve searching speed, we will create a variable representing the div that holds all the commit information
    # This has the class commit full-commit px-2 pt-2

    commit_information_div = page_html.find("div", {"class": "commit full-commit px-2 pt-2"})

    if commit_information_div is not None:  # If this class is none, we don't want to search for the information inside of it
        try:
            # Find commit title

            master_dictionary["commit_title"] = commit_information_div.find("p", {"class": "commit-title"}).text.strip()  # Get commit title from p tag with class='commit-title'

            # Find commit description on the page. This can sometimes be very large, or non-existent

            commit_desc = commit_information_div.find("div", {"class": "commit-desc"})

            if commit_desc is not None:  # This element could not exist in some cases
                master_dictionary["commit_description"] = commit_desc.text.strip()  # Save the commit description text
            else:
                master_dictionary["commit_description"] = "No description provided"

            # Find the author names. These can be one or two people, e.g. manfred-colorfu authored and torvalds committed...

            authors = commit_information_div.find_all("a", {"class": "commit-author tooltipped tooltipped-s user-mention"})
            master_dictionary["author_names"] = [f.text.strip() for f in authors]

            # Find the date and time this commit was authored and pushed
            master_dictionary["datetime"] = commit_information_div.find("relative-time", {"class": "no-wrap"}).get("datetime", default="")  # Find the relative time in the relative-time tag in the commit description div

            # Get the span containing the parent(s) of the commit

            parent_span = commit_information_div.find("span", {"class": "sha-block"})
            master_dictionary["parent_commit_hashes"] = [
                link_tag.get("href").split("/")[-1] for link_tag in parent_span.find_all("a", {"class": "sha"})
            ]  # Find all of the link tags in the span, then get the commit hash from their href values.

            # Get the commit hash of the current commit

            master_dictionary["commit_hash"] = commit_information_div.find("span", {"class": "sha user-select-contain"}).text.strip()  # This span holds the commit hash

        except Exception as e:  # We don't want the program to crash because one of the elements that should exist, doesn't.
            print e

    # Create a variable holding the file div elements on the page

    file_divs = page_html.find("div", {"class": "js-diff-progressive-container"}).find_all("div", recursive=False)

    # Iterate through each file div and extract the necessary data

    for file_div in file_divs:
        try:
            file_data = {
                "file_path": "",
                "change_count": 0,
                "addition_count": 0,
                "deletion_count": 0,
                "blame_link": "",
                "old_lines": {},  # We preserve the old lines. If these are not used elsewhere in the program, this field can be removed and the assigning lines deleted.
                "new_lines": {},  # We preserve the new lines. If these are not used elsewhere in the program, this field can be removed and the assigning lines deleted.
                "inline_diff": {},  # We create an inline diff.
                "split_diff": {}  # We create a split diff. If this is not used elsewhere, this field can be removed and the assigning lines deleted.
            }

            # Find the file path

            file_data["file_path"] = file_div.find("div", {"class": "file-info flex-auto"}).find("a").text.strip()  # Find the name of the file we are looking at

            # Retrieve the number of changes: additions and deletions.

            text_label = file_div.find("span", {"class": "diffstat tooltipped tooltipped-e"}).get("aria-label").strip() # This string is of the form "{x+y} change(s): x addition(s) & y deletion(s)"
            change_counts = [""+f.replace(",", "") for f in re.findall(r"([\d,]+)", text_label)]  # Gather numbers, remove commas if present, and make sure they are regular strings

            file_data["change_count"] = change_counts[0]  # Write total changes
            file_data["addition_count"] = change_counts[1]  # Write additions
            file_data["deletion_count"] = change_counts[2]  # Write deletions

            #  Find the blame link...TODO convert to our blame link.

            link_prefix= "https://github.com/{}/{}/blame/{}".format(master_dictionary["user_name"], master_dictionary["repository_name"], master_dictionary["commit_hash"])  # Replace this prefix with our version at some point
            file_data["blame_link"] = "{}{}".format(link_prefix, file_data["file_path"])

            #  Create line dictionaries and inline diff
            code_body = file_div.find("table")
            x = 0  # Our internal line number value
            for code_line in [f for f in code_body.find_all("tr") if not f.get("class") == ["js-expandable-line"]]:  # We don't want to include expandable lines here, so we eliminate them and return only the lines we want via list comprehension
                elements = code_line.find_all("td")  # Find all td elements. We then need to split this.
                old_line_elem = elements[0].get("data-line-number", default="*")  # We find the old line number, if any
                new_line_elem = elements[1].get("data-line-number", default="*")  # We find the new line number, if any
                line_text = elements[2].text.strip() if elements[2] is not None and elements[2].text is not None else ""  # We get the text, if present. These checks may be unnecessary, but I'm not sure as of yet
                if old_line_elem != "*":
                    file_data["old_lines"][int(old_line_elem)] = line_text  # We assign the text to the line number of the old text in the dictionary
                if new_line_elem != "*":
                    file_data["new_lines"][int(new_line_elem)] = line_text  # We assign the text to the line number of the new text in the dictionary
                file_data["inline_diff"][x] = {
                    "old_text_line_number": old_line_elem,
                    "new_text_line_number": new_line_elem,
                    "text": line_text
                    }
                # DEBUGGING_OUTPUT
                file_data["pretty_diff"] = output_pretty_inline_diff(file_data["inline_diff"])
                x = x+1  # Increment our internal line count by one after we have processed a line
            y = 0  # TODO Create split diff and add to file data
            # Add this processed file to our file dictionary
            master_dictionary["files"][file_data["file_path"]] = file_data

        except Exception as e:  # Catching errors and printing to console
            print e





    return master_dictionary

def output_pretty_inline_diff(diff):
    output_string = []
    internal_lines = diff.keys()
    for dict_entry_key in sorted(internal_lines):
        diff_entry = diff[dict_entry_key]
        output_string.append("{}\t{} |\t{}".format(
            diff_entry["old_text_line_number"],
            diff_entry["new_text_line_number"],
            diff_entry["text"]
            ))
    return output_string

def output_pretty_split_diff(diff):
    output_string = ""


if __name__ == "__main__":
    result = retrieve_commit_page("https://github.com/torvalds/linux/commit/3278a2c20cb302d27e6f6ee45a3f57361176e426")
    print json.dumps(result, indent=4)
    for r in result["files"]:
        print "_______________________________________________________________________________________________"
        print "\n".join(result["files"][r]["pretty_diff"])
        print "_______________________________________________________________________________________________"




def get_commit(repo_user, repo_name, hash):
    data = {}

    link = "https://github.com/{}/{}/commit/{}".format(repo_user, repo_name, hash)

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