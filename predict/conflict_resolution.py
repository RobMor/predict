# Data Processing Helpers File

# ***** NOTE: Asumption is that database entries are of the format:
# (CVE ID, Username, Repo Name, Repo User, Fix Commit, Fix File, Intro Commit, Intro File)

import json
import sqlite3
import predict.cve
import predict.github

import flask
import requests
import flask_login




def processEntries(entries, currentUser):
    """Takes a list of label objects and converts them into a list of blocks of
    subBlocks of dictionaries. Blocks are lists of subBlocks and subBlocks are
    lists of dictionaries. Blocks are unique by CVE ID, subBlocks within a Block
    are unique by username. Dictionaries within a subblock each contain one of
    the user's labels for that cve_id, represented as a dictionary, plus some
    additional information including the Match/Conflict information relative to
    other subBlocks, and the url's for the commit info and blame pages for that
    label's fix/intro hash/file."""
    blocks = splitByCveId(entries)
    for i in range(0, len(blocks)):
        newBlock = blocks[i]
        newBlock = splitByUser(newBlock)
        newBlock = moveUserToFront(newBlock, currentUser)
        containsCurrentUser = newBlock[0][0].username == currentUser
        currUserSubBlock = newBlock[0]
        for j in range(0, len(newBlock)):
            subBlock = newBlock[j]
            subBlock = eliminateRedundancies(subBlock)
            newSubBlock = []
            for k in range(0, len(subBlock)):
                subBlockEntryDict = appendURLs(subBlock[k])
                newSubBlock.append(subBlockEntryDict)
            if j == 0:
                currUserSubBlock = newSubBlock
            if containsCurrentUser:
                if j != 0:
                    newSubBlock = predict.conflict_resolution.insertSubBlockAgreements(
                        newSubBlock, currUserSubBlock
                    )
            else:
                newSubBlock = predict.conflict_resolution.insertSubBlockAgreements(newSubBlock, None)
            newBlock[j] = newSubBlock
        if containsCurrentUser:
            newBlock = predict.conflict_resolution.insertPercentages(newBlock)
        blocks[i] = newBlock
    return blocks



def insertSubBlockAgreements(subBlock, currUserSubBlock):
    """Inserts the Match/Conflict info for the fix/intro file/hash for the
    subBlock relative to the current user's subBlock. Match/Conflict is determined
    by set equality of the subBlock's labels and the current user's labels for
    that cve. If the current user hasn't labeled this cve, then all entries get
    N/A for those fields."""
    if currUserSubBlock is not None:
        fixCommitAgree = "Match" if setEquality(subBlock, currUserSubBlock, "fix_hash") else "Conflict"
        fixFileAgree = "Match" if setEquality(subBlock, currUserSubBlock, "fix_file") else "Conflict"
        introCommitAgree = "Match" if setEquality(subBlock, currUserSubBlock, "intro_hash") else "Conflict"
        introFileAgree = "Match" if setEquality(subBlock, currUserSubBlock, "intro_file") else "Conflict"
    else:
        fixCommitAgree = "N/A"
        fixFileAgree = "N/A"
        introCommitAgree = "N/A"
        introFileAgree = "N/A"
    for i in range(0,len(subBlock)):
        if i == 0:
            subBlock[i] = {"cve_id": subBlock[i]["cve_id"], "username": subBlock[i]["username"],
            "group_num": subBlock[i]["group_num"], "label_num": subBlock[i]["label_num"],
            "repo_name": subBlock[i]["repo_name"], "repo_user": subBlock[i]["repo_user"],
            "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": fixCommitAgree,
            "fix_file": subBlock[i]["fix_file"], "fix_file_agree": fixFileAgree,
            "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": introCommitAgree,
            "intro_file": subBlock[i]["intro_file"], "intro_file_agree": introFileAgree,
            "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
            "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"],
            "comment": subBlock[i]["comment"], "edit_date": subBlock[i]["edit_date"]}
        else:
            subBlock[i] = {"cve_id": subBlock[i]["cve_id"], "username": subBlock[i]["username"],
            "group_num": subBlock[i]["group_num"], "label_num": subBlock[i]["label_num"],
            "repo_name": subBlock[i]["repo_name"], "repo_user": subBlock[i]["repo_user"],
            "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": "",
            "fix_file": subBlock[i]["fix_file"], "fix_file_agree": "",
            "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": "",
            "intro_file": subBlock[i]["intro_file"], "intro_file_agree": "",
            "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
            "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"],
            "comment": subBlock[i]["comment"], "edit_date": subBlock[i]["edit_date"]}

    return subBlock

def appendURLs(entry):
    """Returns a dictionary with the urls to the commit info and blame pages for
    the argument label's fix/intro file/hash fields, along with all the
    existing fields of the object."""
    fixCommitURL = flask.url_for("main.info_page", cve_id=entry.cve_id,
        repo_name = entry.repo_name, repo_user = entry.repo_user,
        commit = entry.fix_hash)
    fixFileURL = flask.url_for("main.info_page", cve_id=entry.cve_id,
        repo_name = entry.repo_name, repo_user = entry.repo_user,
        commit = entry.fix_file)
    introCommitURL = flask.url_for("main.info_page", cve_id=entry.cve_id,
        repo_name = entry.repo_name, repo_user = entry.repo_user,
        commit = entry.intro_hash)
    introFileURL = flask.url_for("main.info_page", cve_id=entry.cve_id,
        repo_name = entry.repo_name, repo_user = entry.repo_user,
        commit = entry.intro_file)
    return {"cve_id": entry.cve_id, "username": entry.username, "repo_name": entry.repo_name,
        "group_num": entry.group_num, "label_num": entry.label_num,
        "repo_user": entry.repo_user, "fix_hash": entry.fix_hash, "fix_file": entry.fix_file,
        "intro_hash": entry.intro_hash, "intro_file": entry.intro_file, "fix_hash_url": fixCommitURL,
        "fix_file_url": fixFileURL, "intro_hash_url": introCommitURL, "intro_file_url": introFileURL,
        "comment": entry.comment, "edit_date": entry.edit_date}

def insertPercentages(block):
    """Calculates the percentage of the other subBlocks in the block that
    match the first subBlock's (which is the current user's subBlock if they have
    labeled this cve) labels and puts those percentages in the first subBlock's
    agreement fields in lieu of Match/Conflict like in all the other subBlocks.
    If the current user hasn't labeled this cve, then N/A is entered for those
    fields instead."""
    length = len(block)-1
    fixCommitCount = 0.0
    fixFileCount = 0.0
    introCommitCount = 0.0
    introFileCount = 0.0
    userEntry = block[0]
    for i in range(0,len(block)):
        if not i == 0:
            if block[i][0]["fix_hash_agree"] == "Match":
                fixCommitCount += 1
            if block[i][0]["fix_file_agree"] == "Match":
                fixFileCount += 1
            if block[i][0]["intro_hash_agree"] == "Match":
                introCommitCount += 1
            if block[i][0]["intro_file_agree"] == "Match":
                introFileCount += 1
    subBlock = block[0]
    for i in range(0,len(subBlock)):
        if length > 0:
            if i == 0:
                subBlock[i] = {"cve_id": subBlock[i]["cve_id"], "username": subBlock[i]["username"],
                "repo_name": subBlock[i]["repo_name"], "repo_user": subBlock[i]["repo_user"],
                "group_num": subBlock[i]["group_num"], "label_num": subBlock[i]["label_num"],
                "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": str(round(fixCommitCount/length*100)) + "%",
                "fix_file": subBlock[i]["fix_file"], "fix_file_agree": str(round(fixFileCount/length*100)) + "%",
                "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": str(round(introCommitCount/length*100)) + "%",
                "intro_file": subBlock[i]["intro_file"], "intro_file_agree": str(round(introFileCount/length*100)) + "%",
                "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
                "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"],
                "comment": subBlock[i]["comment"], "edit_date": subBlock[i]["edit_date"]}
            else:
                subBlock[i] = {"cve_id": subBlock[i]["cve_id"], "username": subBlock[i]["username"],
                "repo_name": subBlock[i]["repo_name"], "repo_user": subBlock[i]["repo_user"],
                "group_num": subBlock[i]["group_num"], "label_num": subBlock[i]["label_num"],
                "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": "",
                "fix_file": subBlock[i]["fix_file"], "fix_file_agree": "",
                "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": "",
                "intro_file": subBlock[i]["intro_file"], "intro_file_agree": "",
                "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
                "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"],
                "comment": subBlock[i]["comment"], "edit_date": subBlock[i]["edit_date"]}
        else:
            if i == 0:
                subBlock[i] = {"cve_id": subBlock[i]["cve_id"], "username": subBlock[i]["username"],
                "repo_name": subBlock[i]["repo_name"], "repo_user": subBlock[i]["repo_user"],
                "group_num": subBlock[i]["group_num"], "label_num": subBlock[i]["label_num"],
                "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": "N/A",
                "fix_file": subBlock[i]["fix_file"], "fix_file_agree": "N/A",
                "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": "N/A",
                "intro_file": subBlock[i]["intro_file"], "intro_file_agree": "N/A",
                "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
                "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"],
                "comment": subBlock[i]["comment"], "edit_date": subBlock[i]["edit_date"]}
            else:
                subBlock[i] = {"cve_id": subBlock[i]["cve_id"], "username": subBlock[i]["username"],
                "repo_name": subBlock[i]["repo_name"], "repo_user": subBlock[i]["repo_user"],
                "group_num": subBlock[i]["group_num"], "label_num": subBlock[i]["label_num"],
                "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": "",
                "fix_file": subBlock[i]["fix_file"], "fix_file_agree": "",
                "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": "",
                "intro_file": subBlock[i]["intro_file"], "intro_file_agree": "",
                "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
                "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"],
                "comment": subBlock[i]["comment"], "edit_date": subBlock[i]["edit_date"]}
    block[0] = subBlock
    return block

def eliminateRedundancies(subBlock):
    """Replaces the cve_id and username wth empty strings for all entrues in the
    subBlocks except the first so that they are not repeatedly displayed within
    the same subBlock, making it much easier for the user to visually identify
    where subBlocks start and end."""
    newSubBlock = []
    for i in range(0, len(subBlock)):
        if i != 0:
            subBlock[i].cve_id = ""
            subBlock[i].username = ""
# The following lines remove duplicate files/hashes within a sub block. Currently
# we are choosing to show raw labels, but these can be uncommented in the future
# if that decision changes.
#            if containsOther(subBlock, subBlock[i].fix_hash, "fix_hash", i):
#                subBlock[i].fix_hash = ""
#            if containsOther(subBlock, subBlock[i].fix_file, "fix_file", i):
#                subBlock[i].fix_file = ""
#            if containsOther(subBlock, subBlock[i].intro_hash, "intro_hash", i):
#                subBlock[i].intro_hash = ""
#            if containsOther(subBlock, subBlock[i].intro_file, "intro_file", i):
#                subBlock[i].intro_file = ""
        newSubBlock.append(subBlock[i])
    return newSubBlock

def moveUserToFront(block, user):
    """If the specified user has labeled the block's cve_id, then that user's
    subBlock of labels is moved to the front of the block."""
    index = -1
    for i in range(0,len(block)):
        if block[i][0].username == user:
            index = i
    if index == -1:
        return block
    subBlock = block[index]
    block.remove(subBlock)
    newBlock = [subBlock]
    newBlock.extend(block)
    return newBlock

# Takes in a list of entries and returns a list of lists of entries, where each inner list contains all entries of a single CVE_ID
# ASSUMES LIST IS SORTED BY CVE_ID
def splitByCveId(entries):
    """Splits a list of labels into a list of blocks by cve_id. Assumes labels
    are sorted by cve_id already."""
    currCVE = ""
    blocks = []
    blockNum = -1
    for i in range(0, len(entries)):
        if entries[i].cve_id != currCVE:
            currCVE = entries[i].cve_id
            blocks.append([])
            blockNum += 1
        blocks[blockNum].append(entries[i])
    return blocks

# Takes in a list of entries of matching cve ids and returns a list of lists of entrues, where each inner list contains all entries of a single users
# ASSUMES LIST IS SORTED BY CVE_ID
def splitByUser(block):
    """Splits a block into subBlocks by username. Assumes block is sorted by
    username already."""
    currUser = ""
    blocks = []
    blockNum = -1
    for i in range(0, len(block)):
        if block[i].username != currUser:
            currUser = block[i].username
            blocks.append([])
            blockNum += 1
        blocks[blockNum].append(block[i])
    return blocks


def setEquality(subBlock1, subBlock2, field):
    """Returns true if all entries for the specified field in subBlock1 are
    contained in subBlock2 AND the entries have the same repo_name and repo_user
     and vice versa, false otherwise."""
    for entry in subBlock1:
        if not contains(subBlock2, entry[field], field, entry["repo_name"], entry["repo_user"]):
            return False

    for entry in subBlock2:
        if not contains(subBlock1, entry[field], field, entry["repo_name"], entry["repo_user"]):
            return False

    return True


def contains(subBlock, element, field, repo_name, repo_user):
    """Checks if the subBlock contains the element passed in for the field passed
    in, for an entry where the repo_name and repo_user also match. True if found
    false otherwise."""
    for i in range(0, len(subBlock)):
        if subBlock[i][field] == element and subBlock[i]["repo_name"] == repo_name and subBlock[i]["repo_user"] == repo_user:
            return True
    return False

def containsOther(subBlock, element, field, index):
    """Same as contains but only checks entries not at the specified index in
    the subBlock. Currently not used, but may be in the future."""
    for i in range(0, len(subBlock)):
        if field == "fix_hash":
            if subBlock[i].fix_hash == element and i != index:
                return True
        if field == "fix_file":
            if subBlock[i].fix_file == element and i != index:
                return True
        if field == "intro_hash":
            if subBlock[i].intro_hash == element and i != index:
                return True
        if field == "intro_file":
            if subBlock[i].intro_file == element and i != index:
                return True
    return False
