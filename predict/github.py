import re
import difflib
import datetime

import flask
import requests
import pygments
import pygments.formatters
import pygments.lexers
from bs4 import BeautifulSoup


def get_commit_info(cve_id, repo_user, repo_name, commit_hash):
    if True: # is_valid_github_link(repo_user, repo_name, commit_hash):
        entry_in_cache = False

        if entry_in_cache:
            # TODO Retrieve the entry from the cache here...
            return None
        else:
            raw_commit = scrape_commit_info(repo_user, repo_name, commit_hash)
            if raw_commit is not None:
                return process_commit_info(cve_id, raw_commit)

    return None


def scrape_commit_info(repo_user, repo_name, commit_hash):
    github_data = {
        "repo_user": repo_user,
        "repo_name": repo_name,
        "hash": commit_hash,
    }

    url = f"https://github.com/{repo_user}/{repo_name}/commit/{commit_hash}"

    # Getting a split diff to make parsing diffs easier
    response = requests.get(url, params={"diff": "split"})
    page_html = BeautifulSoup(response.text, "html.parser")

    # TODO check to see what happens when an invalid commit is given

    # Get the div containing commit information to improve searching speeds
    commit_information_div = page_html.find("div", {"class": "full-commit"})

    github_data["title"] = commit_information_div.find(
        "p", {"class": "commit-title"}
    ).text.strip()

    # This element could not exist in some cases
    commit_desc = commit_information_div.find("div", {"class": "commit-desc"})
    if commit_desc is not None:
        github_data["desc"] = commit_desc.text.strip()
    else:
        github_data["desc"] = "No description provided"

    authors = commit_information_div.find_all("a", {"class": "commit-author"})
    github_data["authors"] = [f.text.strip() for f in authors]

    # Parse datetime by cutting out the Z at the end
    github_data["datetime"] = datetime.datetime.fromisoformat(
        commit_information_div.find("relative-time", {"class": "no-wrap"})["datetime"][
            :-1
        ]
    )

    # NOTE I don't think we have a use for parent commits when appending a ^ works fine
    # Get the span containing the parent(s) of the commit
    # parent_span = commit_information_div.find("span", {"class": "sha-block"})
    # master_dictionary["parent_commit_hashes"] = [
    #     link_tag.get("href").split("/")[-1] for link_tag in parent_span.find_all("a", {"class": "sha"})
    # ]  # Find all of the link tags in the span, then get the commit hash from their href values.

    # Find all the file divs
    file_divs = page_html.find(
        "div", {"class": "js-diff-progressive-container"}
    ).find_all("div", recursive=False)

    github_data["files"] = []
    for file_div in file_divs:
        file_data = {}

        # Find the file path
        file_data["path"] = file_div.find("div", {"class": "file-header"})["data-path"]

        # NOTE we are probably safe without number of changes too
        # # Retrieve the number of changes: additions and deletions.
        # text_label = file_div.find("span", {"class": "diffstat tooltipped tooltipped-e"}).get("aria-label").strip() # This string is of the form "{x+y} change(s): x addition(s) & y deletion(s)"
        # change_counts = [""+f.replace(",", "") for f in re.findall(r"([\d,]+)", text_label)]  # Gather numbers, remove commas if present, and make sure they are regular strings

        # file_data["change_count"] = change_counts[0]  # Write total changes
        # file_data["addition_count"] = change_counts[1]  # Write additions
        # file_data["deletion_count"] = change_counts[2]  # Write deletions

        file_data["github_link"] = url + "/" + file_data["path"]

        # NOTE probably don't need this either
        # # Find the history link
        # link_prefix = "https://github.com/{}/{}/commits/{}/".format(master_dictionary["user_name"], master_dictionary["repository_name"], master_dictionary["commit_hash"])  # Replace this prefix with our version at some point
        # file_data["history_link"] = "{}{}".format(link_prefix, file_data["file_path"])

        code_body = file_div.find("table")
        lines = code_body.find_all("tr")

        file_data["groups"] = []

        # Get the part between the two @@'s
        match = re.search(
            "@@\s+\-(\d+),\d+\s\+(\d+),\d+\s+@@",
            lines[0].find("td", {"class": "blob-code"}).text,
        )

        # If the first row is the @@ thing
        if match is not None:
            current_group_old_start = int(match[1])
            current_group_new_start = int(match[2])
            lines = lines[1:] # Skip the first row
        else:
            current_group_old_start = 1
            current_group_new_start = 1

        current_group_old = []
        current_group_new = []
        
        for line in lines:
            if line.has_attr("data-position"):
                file_data["groups"].append(
                    {
                        "old_start": current_group_old_start,
                        "new_start": current_group_new_start,
                        "old_code": "".join(current_group_old),
                        "new_code": "".join(current_group_new),
                    }
                )

                match = re.search(
                    "@@\s+\-(\d+),\d+\s\+(\d+),\d+\s+@@",
                    line.find("td", {"class": "blob-code"}).text,
                )

                # The last row will not have @@ in it
                if match is not None:
                    current_group_old_start = int(match[1])
                    current_group_new_start = int(match[2])
                    current_group_old = []
                    current_group_new = []
            else:
                old_code, new_code = tuple(line.find_all("td", {"class": "blob-code"}))

                if old_code.text:
                    old_code = old_code.text
                    if old_code.startswith("\n"):
                        old_code = old_code[1:]
                    current_group_old.append(old_code)

                if new_code.text:
                    new_code = new_code.text
                    if new_code.startswith("\n"):
                        new_code = new_code[1:]
                    current_group_new.append(new_code)

        # Add the last group if it wasn't already added
        # TODO better condition
        if match is not None:
            file_data["groups"].append(
                    {
                        "old_start": current_group_old_start,
                        "new_start": current_group_new_start,
                        "old_code": "".join(current_group_old),
                        "new_code": "".join(current_group_new),
                    }
                )

        github_data["files"].append(file_data)

    return github_data


def process_commit_info(cve_id, commit_info):
    formatter = pygments.formatters.HtmlFormatter(nowrap=True)

    for file in commit_info["files"]:
        file["blame_link"] = flask.url_for(
            "main.blame_page",
            cve_id=cve_id,
            repo_user=commit_info["repo_user"],
            repo_name=commit_info["repo_name"],
            commit=commit_info["hash"],
            file_name=file["path"],
        )

        for group in file["groups"]:
            group["diff"] = difflib.SequenceMatcher(None, group["old_code"].splitlines(True), group["new_code"].splitlines(True)).get_opcodes()

            lexer = pygments.lexers.get_lexer_for_filename(file["path"])
            group["old_code"] = pygments.highlight(
                group["old_code"], lexer, formatter
            ).splitlines(True)
            group["new_code"] = pygments.highlight(
                group["new_code"], lexer, formatter
            ).splitlines(True)

    return commit_info


def get_blame_page(cve_id, repo_user, repo_name, comm_hash, file_name):
    # Initialize variables
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
        "sorted_block_numbers": [],
        "page_html": "",
    }  # Create a dictionary that we will return, containing the important information on the page

    link = "https://github.com/{}/{}/blame/{}/{}".format(
        repo_user, repo_name, comm_hash, file_name
    )

    response = requests.get(link)
    page_html = BeautifulSoup(
        response.text, "html.parser"
    )  # Get a manipulable representation of the page HTML with bs4
    # master_dictionary["page_html"] = page_html.prettify()  # Preserve the html page, just in case

    # Debugging output, can be removed
    # print page_html.prettify()

    # We need a diff. To get this, we will look at the entire commit page, for lack of a better option. This should be removed eventually and replaced with a faster method like caching the diff from the commit page

    result = retrieve_commit_page(cve_id, repo_user, repo_name, comm_hash)
    master_dictionary["inline_diff"] = (
        result.get("files", {}).get(file_name, {}).get("inline_diff", {})
    )
    master_dictionary["split_diff"] = (
        result.get("files", {}).get(file_name, {}).get("split_diff", {})
    )
    master_dictionary["sorted_line_numbers"] = (
        result.get("files", {}).get(file_name, {}).get("sorted_line_numbers", {})
    )

    # print(page_html)
    master_dictionary["line_count"] = re.findall(
        r"([\d,]+) lines", page_html.find("div", {"class": "file-info"}).text
    )[0].replace(
        ",", ""
    )  # We find the line count of the file we are looking at using regex
    master_dictionary["file_size"] = re.findall(
        r"[\d,\.]+ [KMGkmg]?[Bb](?:ytes)?",
        page_html.find("div", {"class": "file-info"}).text,
    )[0].replace(
        ",", ""
    )  # We find the size of the file we are looking at using regex

    # Now we need to get to the code blocks
    # Create a variable to hold the div above, reducing look time

    code_hunk_div = page_html.find("div", {"class": "blob-wrapper"})

    # Iterate through code hunks and add them to the lines field in our dictionary
    x = 0
    print(
        code_hunk_div.find_all(
            "div", {"class": "blame-hunk d-flex border-gray-light border-bottom"}
        )
    )
    for code_hunk in code_hunk_div.find_all(
        "div", {"class": "blame-hunk d-flex border-gray-light border-bottom"}
    ):

        # Now we possess a code hunk. We need to go through this, separate out lines, and match them with a blame commit, timestamp and reblame link.

        blame_hunk = code_hunk.find(
            "div", {"class": "blame-commit flex-self-stretch mr-1"}
        )  # Create a hunk variable to limit searching

        blame_commit_message = blame_hunk.find(
            "div", {"class": "blame-commit-content d-flex no-wrap flex-items-center"}
        ).text.strip()
        blame_commit_time = blame_hunk.find("time-ago").get("datetime")

        # Format the link

        our_link_format = "/cve/{}/blame".format(
            cve_id
        )  # If we change our link format, change this

        a_tag = code_hunk.find("div", {"class": "blob-reblame pl-1 pr-1"}).find("a")
        link_base = ""
        if a_tag is not None:
            link_base = a_tag.get("href").replace("blame/", "")
        blame_commit_link = "{}{}".format(our_link_format, link_base)
        master_dictionary["block_representation"][x] = {
            "blame_commit_message": blame_commit_message,
            "blame_commit_time": blame_commit_time,
            "blame_commit_link": blame_commit_link,
            "text": code_hunk.find("div", {"class": "width-full"}).text.strip(),
        }

        # Now we need to create a dictionary for each line, and then add those to the lines field
        print(
            code_hunk.find_all(
                "div", {"class": "d-flex flex-justify-start flex-items-start"}
            )
        )
        for blame_line in code_hunk.find_all(
            "div", {"class": "d-flex flex-justify-start flex-items-start"}
        ):
            line_number = int(
                blame_line.find(
                    "div",
                    {"class": "blob-num blame-blob-num bg-gray-light js-line-number"},
                ).text.strip()
            )
            line_text = blame_line.find(
                "div", {"class": "blob-code blob-code-inner js-file-line"}
            ).text.strip()
            master_dictionary["line_representation"][line_number] = {
                "blame_commit_message": blame_commit_message,
                "blame_commit_time": blame_commit_time,
                "blame_commit_link": blame_commit_link,
                "line_number": line_number,
                "line_text": line_text.strip(),
            }
        master_dictionary["sorted_block_numbers"].append(x)
        x = x + 1
    master_dictionary["sorted_blame_line_numbers"] = sorted(
        master_dictionary["line_representation"].keys()
    )
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
