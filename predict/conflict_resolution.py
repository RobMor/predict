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
            subBlock[i] = {"cve": subBlock[i]["cve"], "username": subBlock[i]["username"],
            "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": fixCommitAgree,
            "fix_file": subBlock[i]["fix_file"], "fix_file_agree": fixFileAgree,
            "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": introCommitAgree,
            "intro_file": subBlock[i]["intro_file"], "intro_file_agree": introFileAgree,
            "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
            "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"]}
        else:
            subBlock[i] = {"cve": subBlock[i]["cve"], "username": subBlock[i]["username"],
            "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": "",
            "fix_file": subBlock[i]["fix_file"], "fix_file_agree": "",
            "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": "",
            "intro_file": subBlock[i]["intro_file"], "intro_file_agree": "",
            "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
            "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"]}

    return subBlock

def appendURLs(entry):
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
    return {"cve": entry.cve_id, "username": entry.username, "repo_name": entry.repo_name,
        "repo_user": entry.repo_user, "fix_hash": entry.fix_hash, "fix_file": entry.fix_file,
        "intro_hash": entry.intro_hash, "intro_file": entry.intro_file, "fix_hash_url": fixCommitURL,
        "fix_file_url": fixFileURL, "intro_hash_url": introCommitURL, "intro_file_url": introFileURL}

def insertPercentages(block):
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
                subBlock[i] = {"cve": subBlock[i]["cve"], "username": subBlock[i]["username"],
                "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": str(round(fixCommitCount/length*100)) + "%",
                "fix_file": subBlock[i]["fix_file"], "fix_file_agree": str(round(fixFileCount/length*100)) + "%",
                "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": str(round(introCommitCount/length*100)) + "%",
                "intro_file": subBlock[i]["intro_file"], "intro_file_agree": str(round(introFileCount/length*100)) + "%",
                "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
                "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"]}
            else:
                subBlock[i] = {"cve": subBlock[i]["cve"], "username": subBlock[i]["username"],
                "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": "",
                "fix_file": subBlock[i]["fix_file"], "fix_file_agree": "",
                "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": "",
                "intro_file": subBlock[i]["intro_file"], "intro_file_agree": "",
                "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
                "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"]}
        else:
            if i == 0:
                subBlock[i] = {"cve": subBlock[i]["cve"], "username": subBlock[i]["username"],
                "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": "N/A",
                "fix_file": subBlock[i]["fix_file"], "fix_file_agree": "N/A",
                "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": "N/A",
                "intro_file": subBlock[i]["intro_file"], "intro_file_agree": "N/A",
                "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
                "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"]}
            else:
                subBlock[i] = {"cve": subBlock[i]["cve"], "username": subBlock[i]["username"],
                "fix_hash": subBlock[i]["fix_hash"], "fix_hash_agree": "",
                "fix_file": subBlock[i]["fix_file"], "fix_file_agree": "",
                "intro_hash": subBlock[i]["intro_hash"], "intro_hash_agree": "",
                "intro_file": subBlock[i]["intro_file"], "intro_file_agree": "",
                "fix_hash_url": subBlock[i]["fix_hash_url"], "fix_file_url": subBlock[i]["fix_file_url"],
                "intro_hash_url": subBlock[i]["intro_hash_url"], "intro_file_url": subBlock[i]["intro_file_url"]}
    block[0] = subBlock
    return block

def eliminateRedundancies(subBlock):
    newSubBlock = []
    for i in range(0, len(subBlock)):
        if i != 0:
            subBlock[i].cve = ""
            subBlock[i].username = ""
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
    for entry in subBlock1:
        if not contains(subBlock2, entry[field], field):
            return False

    for entry in subBlock2:
        if not contains(subBlock1, entry[field], field):
            return False

    return True


def contains(subBlock, element, field):
    for entry in subBlock:
        if entry[field] == element:
            return True
    return False

def containsOther(subBlock, element, field, index):
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
