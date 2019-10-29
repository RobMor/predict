from bs4 import BeautifulSoup
import requests
import json
import re


def retrieve_commit_page(cve_id, repo_user, repo_name, comm_hash):
    our_link_format = "/cve/{}/blame".format(cve_id)  # If we change our link format, change this
    # Initialize variables
    master_dictionary = {
        "user_name": repo_user,
        "repository_name": repo_name,
        "commit_hash": comm_hash,
        "commit_description": "",
        "commit_title": "",
        "author_names": [],
        "datetime": "",
        "files": {},
        "parent_commit_hashes": [],
        "page_html": ""
    }  # Create a dictionary that we will return, containing the important information on the page

    link = "https://github.com/{}/{}/commit/{}".format(repo_user, repo_name, comm_hash)

    response = requests.get(link)
    page_html = BeautifulSoup(response.text, "html.parser")  # Get a manipulable representation of the page HTML with bs4
    master_dictionary["page_html"] = page_html.prettify()  # Preserve the html page, just in case

    # Debugging output, can be removed
    #print page_html.prettify()

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

        except Exception as e:  # We don't want the program to crash because one of the elements that should exist, doesn't.
            print(e)

    # Create a variable holding the file div elements on the page

    file_divs = page_html.find("div", {"class": "js-diff-progressive-container"}).find_all("div", recursive=False)

    # Iterate through each file div and extract the necessary data

    for file_div in file_divs:
        try:
            file_data = {
                "file_path": "",
                "file_link":"",
                "history_link":"",
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

            # Find the file link

            link_prefix = "https://github.com/{}/{}/blob/{}/".format(master_dictionary["user_name"], master_dictionary["repository_name"], master_dictionary["commit_hash"])  # Replace this prefix with our version at some point
            file_data["file_link"] = "{}{}".format(link_prefix, file_data["file_path"])

            # Find the history link
            link_prefix = "https://github.com/{}/{}/commits/{}/".format(master_dictionary["user_name"], master_dictionary["repository_name"], master_dictionary["commit_hash"])  # Replace this prefix with our version at some point
            file_data["history_link"] = "{}{}".format(link_prefix, file_data["file_path"])

            #  Find the blame link...TODO convert to our blame link.

            link_prefix= "{}/{}/{}/{}/".format(our_link_format, master_dictionary["user_name"], master_dictionary["repository_name"], master_dictionary["commit_hash"])  # Replace this prefix with our version at some point
            file_data["blame_link"] = "{}{}".format(link_prefix, file_data["file_path"].replace("/", "$"))

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
                file_data["sorted_line_numbers"] = sorted(file_data["inline_diff"].keys())
                x = x+1  # Increment our internal line count by one after we have processed a line
            y = 0  # TODO Create split diff and add to file data
            # Add this processed file to our file dictionary
            master_dictionary["files"][file_data["file_path"]] = file_data

        except Exception as e:  # Catching errors and printing to console
            print(e)

    return master_dictionary

def get_blame_page(cve_id, repo_user, repo_name, comm_hash, file_name_ref):
    # Initialize variables
    file_name = file_name_ref.replace("$", "/")

    master_dictionary = {
        "user_name": repo_user,
        "repository_name": repo_name,
        "commit_hash": comm_hash,
        "file_name": file_name,
        "line_count": 0,
        "file_size": "",
        "inline_diff": "",
        "split_diff": "",
        "line_representation": {},
        "block_representation": {},
        "sorted_lines": [],
        "sorted_block_numbers":[],
        "page_html": ""
    }  # Create a dictionary that we will return, containing the important information on the page
    # Our file name should come to us with $ replacing the / characters, because we cannot put it in a link otherwise. So we replace those



    link = "https://github.com/{}/{}/blame/{}/{}".format(repo_user, repo_name, comm_hash, file_name)

    response = requests.get(link)
    page_html = BeautifulSoup(response.text, "html.parser")  # Get a manipulable representation of the page HTML with bs4
    #master_dictionary["page_html"] = page_html.prettify()  # Preserve the html page, just in case

    # Debugging output, can be removed
    # print page_html.prettify()

    # We need a diff. To get this, we will look at the entire commit page, for lack of a better option. This should be removed eventually and replaced with a faster method like caching the diff from the commit page

    result = retrieve_commit_page(cve_id, repo_user, repo_name, comm_hash)
    master_dictionary["inline_diff"] = result.get("files", {}).get(file_name, {}).get("inline_diff", {})
    master_dictionary["split_diff"] = result.get("files", {}).get(file_name, {}).get("split_diff", {})
    master_dictionary["sorted_line_numbers"] = result.get("files", {}).get(file_name, {}).get("sorted_line_numbers", {})

    #print(page_html)
    master_dictionary["line_count"] = re.findall(r"([\d,]+) lines", page_html.find("div", {"class": "file-info"}).text)[0].replace(",", "")  # We find the line count of the file we are looking at using regex
    master_dictionary["file_size"] = re.findall(r"[\d,\.]+ [KMGkmg]?[Bb](?:ytes)?", page_html.find("div", {"class": "file-info"}).text)[0].replace(",", "")  # We find the size of the file we are looking at using regex

    # Now we need to get to the code blocks
    # Create a variable to hold the div above, reducing look time

    code_hunk_div = page_html.find("div", {"class": "blob-wrapper"})

    # Iterate through code hunks and add them to the lines field in our dictionary
    x = 0
    print(code_hunk_div.find_all("div", {"class": "blame-hunk d-flex border-gray-light border-bottom"}))
    for code_hunk in code_hunk_div.find_all("div", {"class": "blame-hunk d-flex border-gray-light border-bottom"}):

        # Now we possess a code hunk. We need to go through this, separate out lines, and match them with a blame commit, timestamp and reblame link.

        blame_hunk = code_hunk.find("div", {"class": "blame-commit flex-self-stretch mr-1"})  # Create a hunk variable to limit searching

        blame_commit_message = blame_hunk.find("div", {"class": "blame-commit-content d-flex no-wrap flex-items-center"}).text.strip()
        blame_commit_time = blame_hunk.find("time-ago").get("datetime")

        # Format the link

        our_link_format = "/cve/{}/blame".format(cve_id)  # If we change our link format, change this

        a_tag = code_hunk.find("div", {"class": "blob-reblame pl-1 pr-1"}).find("a")
        link_base = ""
        if a_tag is not None:
            link_base = a_tag.get("href").replace("blame/", "")
        blame_commit_link = "{}{}".format(our_link_format, link_base)
        master_dictionary["block_representation"][x] ={
            "blame_commit_message": blame_commit_message,
            "blame_commit_time": blame_commit_time,
            "blame_commit_link": blame_commit_link,
            "text": code_hunk.find("div", {"class": "width-full"}).text.strip()
        }

        # Now we need to create a dictionary for each line, and then add those to the lines field
        print(code_hunk.find_all("div", {"class": "d-flex flex-justify-start flex-items-start"}))
        for blame_line in code_hunk.find_all("div", {"class": "d-flex flex-justify-start flex-items-start"}):
            line_number = int(blame_line.find("div", {"class": "blob-num blame-blob-num bg-gray-light js-line-number"}).text.strip())
            line_text = blame_line.find("div", {"class": "blob-code blob-code-inner js-file-line"}).text.strip()
            master_dictionary["line_representation"][line_number] = {
                "blame_commit_message": blame_commit_message,
                "blame_commit_time": blame_commit_time,
                "blame_commit_link": blame_commit_link,
                "line_number": line_number,
                "line_text": line_text.strip()
            }
        master_dictionary["sorted_block_numbers"].append(x)
        x = x+1
    master_dictionary["sorted_blame_line_numbers"] = sorted(master_dictionary["line_representation"].keys())
    return master_dictionary

# def get_commit(repo_user, repo_name, hash):
#     data = {}
#
#     link = "https://github.com/{}/{}/commit/{}".format(repo_user, repo_name, hash)
#
#     response = requests.get(link)
#     soup = BeautifulSoup(response.text, "html.parser")
#
#     data["hash"] = hash
#     data["msg"] = soup.find("div", {"class": "commit-desc"}).text
#
#     file_headers = soup.find_all(
#         "div",
#         {
#             "class": "file-header d-flex flex-items-center file-header--expandable js-file-header"
#         },
#     )
#
#     data["files"] = []
#     # print file_headers
#     for file_header in file_headers:
#         file_name = (
#             file_header.find("div", {"class": "file-info flex-auto"})
#             .find("a", {"class": "link-gray-dark"})
#             .text
#         )
#         try:
#             file_link_div = file_header.find("div", {"class": "file-actions pt-0"})
#             if file_link_div is not None:
#                 file_link = "http://github.com{}".format(
#                     file_link_div.find("a").get("href")
#                 )
#                 blame_link = file_link.replace("blob", "blame")
#                 history_link = file_link.replace("blob", "commits")
#
#                 data["files"].append(
#                     {
#                         "file_name": file_name,
#                         "file_link": file_link,
#                         "blame_link": blame_link,
#                         "history_link": history_link,
#                     }
#                 )
#         except Exception as file_header_exc:
#             print(file_header_exc)
#
#     return data
#
#
# def get_blame(repo_user, repo_name, hash, file_name):
#     # TODO
#     pass

if __name__ == "__main__":
    print(json.dumps(get_blame_page("CVE-2015-8474","redmine", "redmine", "032f2c9be6520d9d1a1608aa4f1d5d1f184f2472", "app$controllers$application_controller.rb"), indent=4))