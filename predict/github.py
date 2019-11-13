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
    if True:  # is_valid_github_link(repo_user, repo_name, commit_hash):
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
    if repo_name is None or repo_user is None or commit_hash is None:
        return None
    github_data = {"repo_user": repo_user, "repo_name": repo_name, "hash": commit_hash}

    url = f"https://github.com/{repo_user}/{repo_name}/commit/{commit_hash}"

    # Getting a split diff to make parsing diffs easier
    response = requests.get(url, params={"diff": "split"})
    special_text = re.sub(r'(\</?)(?:span([^\>]*))(\>)', r'\1pre\2\3', response.text)
    page_html = BeautifulSoup(special_text, "html.parser")
    if page_html.find("img", {"alt": "404 “This is not the web page you are looking for”"}):
        return None
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
            lines = lines[1:]  # Skip the first row
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
                        "old_code": "\n".join(current_group_old),
                        "new_code": "\n".join(current_group_new),
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
                    old_code = old_code.text.replace("\n","")
                    current_group_old.append(old_code)

                if new_code.text:
                    new_code = new_code.text.replace("\n", "")
                    current_group_new.append(new_code)

        # Add the last group if it wasn't already added
        # TODO better condition
        if match is not None:
            file_data["groups"].append(
                {
                    "old_start": current_group_old_start,
                    "new_start": current_group_new_start,
                    "old_code": "\n".join(current_group_old),
                    "new_code": "\n".join(current_group_new),
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
            group["diff"] = difflib.SequenceMatcher(
                None,
                group["old_code"].splitlines(True),
                group["new_code"].splitlines(True),
            ).get_opcodes()

            lexer = pygments.lexers.get_lexer_for_filename(file["path"], stripnl=False)

            group["old_code"] = pygments.highlight(
                group["old_code"], lexer, formatter
            ).splitlines(True)

            group["new_code"] = pygments.highlight(
                group["new_code"], lexer, formatter
            ).splitlines(True)

    return commit_info


def get_blame(cve_id, repo_user, repo_name, commit_hash, file_name):
    if True:  # is_valid_blame_link(repo_user, repo_name, commit_hash):
        entry_in_cache = False

        if entry_in_cache:
            # TODO Retrieve the entry from the cache here...
            return None
        else:
            try:
                raw_blame = scrape_blame(cve_id, repo_user, repo_name, commit_hash, file_name)
                if raw_blame is not None:
                    return process_blame(raw_blame)
            except Exception as error:
                return error
    return None

def scrape_blame(cve_id, repo_user, repo_name, commit_hash, file_name):
    if repo_name is None or repo_user is None or commit_hash is None or file_name is None:
        return None
    blame_data = {
        "user_name": repo_user,
        "repository_name": repo_name,
        "commit_hash": commit_hash,
        "file_name": file_name,
    }

    raw_url = f"https://raw.githubusercontent.com/{repo_user}/{repo_name}/{commit_hash}^/{file_name}"
    raw_text = requests.get(raw_url).text.splitlines(True)
    blame_data["old_code"] = raw_text

    url = f"https://github.com/{repo_user}/{repo_name}/blame/{commit_hash}/{file_name}"
    response = requests.get(url)
    special_text = re.sub(r'(\<div[^\>]*\>)([^\<\n]+)', r'\1<pre>\2</pre>', response.text)
    special_text = re.sub(r'(\</?)(?:span([^\>]*))(\>)', r'\1pre\2\3', special_text)
    soup = BeautifulSoup(special_text, "html.parser")
    if soup.find("img", {"alt": "404 “This is not the web page you are looking for”"}):
        return None
    blame_data["blame_meta"] = []
    blame_data["new_code"] = []
    x = 0
    for blame_hunk in soup.find_all("div", {"class": "blame-hunk"}):
        desc = blame_hunk.find("div", {"class": "blame-commit-message"}).text

        date = blame_hunk.find("div", {"class": "blame-commit-date"}).find("time-ago")["datetime"]
        date = datetime.datetime.fromisoformat(date[:-1])

        blamed_commit_hash = (
            blame_hunk.find("div", {"class": "blame-commit-message"})
            .find("a")["href"]
            .split("/")[-1]
        )

        blamed_commit_url = flask.url_for(
            "main.info_page",
            cve_id=cve_id,
            repo_user=repo_user,
            repo_name=repo_name,
            commit=blamed_commit_hash,
        )

        blamed_blame_url = blame_hunk.find("div", {"class": "blob-reblame"}).find("a")
        if blamed_blame_url is not None:
            blamed_blame_url = blamed_blame_url["href"].split("/")[4:]
            blamed_blame_commit_hash = blamed_blame_url[0]
            blamed_blame_file_name = "/".join(blamed_blame_url[1:])

            blamed_blame_url = flask.url_for(
                "main.blame_page",
                cve_id=cve_id,
                repo_user=repo_user,
                repo_name=repo_name,
                commit=blamed_blame_commit_hash,
                file_name=blamed_blame_file_name,
            )

        blame_meta = {
            "commit_desc": desc,
            "commit_datetime": date,
            "commit_url": blamed_commit_url,
            "blame_url": blamed_blame_url,
        }

        for line in blame_hunk.find_all("div", {"class": "blob-code"}):
            if not line.text.endswith("\n"):
                blame_data["new_code"].append(line.text+"\n")
            else:
                blame_data["new_code"].append(line.text)
            blame_data["blame_meta"].append(blame_meta)
            x+=1

    return blame_data


def process_blame(blame_data):
    blame_data["diff"] = difflib.SequenceMatcher(lambda x: x in " \t", blame_data["old_code"], blame_data["new_code"]).get_opcodes()

    formatter = pygments.formatters.HtmlFormatter(nowrap=True)
    lexer = pygments.lexers.get_lexer_for_filename(blame_data["file_name"])

    blame_data["old_code"] = pygments.highlight("".join(blame_data["old_code"]), lexer, formatter).splitlines(True)
    blame_data["new_code"] = pygments.highlight("".join(blame_data["new_code"]), lexer, formatter).splitlines(True)

    return blame_data
