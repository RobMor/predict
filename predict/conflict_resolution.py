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

# Need 0-7 from database query
CVE_ID_INDEX = 0
USERNAME_INDEX = 1
REPO_NAME_INDEX = 2
REPO_USER_INDEX = 3
FIX_COMMIT_INDEX = 4
FIX_FILE_INDEX = 5
INTRO_COMMIT_INDEX = 6
INTRO_FILE_INDEX = 7
FIX_COMMIT_URL_INDEX = 8
FIX_FILE_URL_INDEX = 9
INTRO_COMMIT_URL_INDEX = 10
INTRO_FILE_URL_INDEX = 11


## *** TODO: FIgure out hwo to clean up these long-ass lines of code without screwing up python indenting!

def insertAgreements(entry, currUserEntry):
    if currUserEntry is not None:
        fixCommitAgree = "Match" if entry[FIX_COMMIT_INDEX] == currUserEntry[FIX_COMMIT_INDEX] else "Conflict"
        fixFileAgree = "Match" if entry[FIX_FILE_INDEX] == currUserEntry[FIX_FILE_INDEX] else "Conflict"
        introCommitAgree = "Match" if entry[INTRO_COMMIT_INDEX] == currUserEntry[INTRO_COMMIT_INDEX] else "Conflict"
        introFileAgree = "Match" if entry[INTRO_FILE_INDEX] == currUserEntry[INTRO_FILE_INDEX] else "Conflict"
    else:
        fixCommitAgree = "N/A"
        fixFileAgree = "N/A"
        introCommitAgree = "N/A"
        introFileAgree = "N/A"
    return (entry[CVE_ID_INDEX], entry[USERNAME_INDEX], entry[FIX_COMMIT_INDEX],
        fixCommitAgree, entry[FIX_FILE_INDEX], fixFileAgree,
        entry[INTRO_COMMIT_INDEX], introCommitAgree, entry[INTRO_FILE_INDEX],
        introFileAgree, entry[FIX_COMMIT_URL_INDEX], entry[FIX_FILE_URL_INDEX],
        entry[INTRO_COMMIT_URL_INDEX], entry[INTRO_FILE_URL_INDEX])

def appendURLs(entry):
    fixCommitURL = flask.url_for("info_page", cve_id = entry[CVE_ID_INDEX],
        repo_name = entry[REPO_NAME_INDEX], repo_user = entry[REPO_USER_INDEX],
        commit = entry[FIX_COMMIT_INDEX])
    fixFileURL = flask.url_for("info_page", cve_id = entry[CVE_ID_INDEX],
        repo_name = entry[REPO_NAME_INDEX], repo_user = entry[REPO_USER_INDEX],
        commit = entry[FIX_FILE_INDEX])
    introCommitURL = flask.url_for("info_page", cve_id = entry[CVE_ID_INDEX],
        repo_name = entry[REPO_NAME_INDEX], repo_user = entry[REPO_USER_INDEX],
        commit = entry[INTRO_COMMIT_INDEX])
    introFileURL = flask.url_for("info_page", cve_id = entry[CVE_ID_INDEX],
        repo_name = entry[REPO_NAME_INDEX], repo_user = entry[REPO_USER_INDEX],
        commit = entry[INTRO_FILE_INDEX])
    return (entry[CVE_ID_INDEX], entry[USERNAME_INDEX], entry[REPO_NAME_INDEX],
        entry[REPO_USER_INDEX], entry[FIX_COMMIT_INDEX], entry[FIX_FILE_INDEX],
        entry[INTRO_COMMIT_INDEX], entry[INTRO_FILE_INDEX], fixCommitURL,
        fixFileURL, introCommitURL, introFileURL)

def insertPercentages(block):
    length = len(block)-1
    fixCommitCount = 0.0
    fixFileCount = 0.0
    introCommitCount = 0.0
    introFileCount = 0.0
    userEntry = block[0]
    newBlock = block
    for entry in block:
        if entry != block[0]:
            print(entry)
            if entry[USERNAME_INDEX] != userEntry[USERNAME_INDEX] and entry[3] == "Match":
                fixCommitCount += 1
            if entry[USERNAME_INDEX] != userEntry[USERNAME_INDEX] and entry[5] == "Match":
                fixFileCount += 1
            if entry[USERNAME_INDEX] != userEntry[USERNAME_INDEX] and entry[7] == "Match":
                introCommitCount += 1
            if entry[USERNAME_INDEX] != userEntry[USERNAME_INDEX] and entry[9] == "Match":
                introFileCount += 1
    if length > 0:
        newBlock[0] =(newBlock[0][CVE_ID_INDEX], newBlock[0][USERNAME_INDEX],
            newBlock[0][FIX_COMMIT_INDEX], str(round(fixCommitCount/length*100)) + "%",
            newBlock[0][FIX_FILE_INDEX], str(round(fixFileCount/length*100)) + "%",
            newBlock[0][INTRO_COMMIT_INDEX], str(round(introCommitCount/length*100)) + "%",
            newBlock[0][INTRO_FILE_INDEX], str(round(introFileCount/length*100)) + "%",
            newBlock[0][FIX_COMMIT_URL_INDEX], newBlock[0][FIX_FILE_URL_INDEX],
            newBlock[0][INTRO_COMMIT_URL_INDEX], newBlock[0][INTRO_FILE_URL_INDEX])
    else:
        newBlock[0] =(newBlock[0][CVE_ID_INDEX], newBlock[0][USERNAME_INDEX],
        newBlock[0][FIX_COMMIT_INDEX], "N/A", newBlock[0][FIX_FILE_INDEX], "N/A",
        newBlock[0][INTRO_COMMIT_INDEX], "N/A", newBlock[0][INTRO_FILE_INDEX], "N/A")
    return newBlock


# Assumes all entries are of the same CVE_ID, and for unique users (NO DUPLICATE USERS FOR SAME CVE ENTRY SHOULD BE IN DATABASE!!!)
def moveUserToFront(entries, user):
    index = -1
    for i in range(0,len(entries)):
        if entries[i][USERNAME_INDEX] == user:
            index = i
    if index == -1:
        return entries
    entry = entries[index]
    entries.remove(entry)
    newEntries = [entry]
    newEntries.extend(entries)
    return newEntries

# Takes in a list of entries and returns a list of lists of entries, where each inner list contains all entries of a single CVE_ID
# ASSUMES LIST iS SORTED BY CVE_ID
def splitByCveId(entries):
    currCVE = ""
    blocks = []
    blockNum = -1
    i = 0
    for entry in entries:
        if entry[CVE_ID_INDEX] != currCVE:
            currCVE = entries[i][CVE_ID_INDEX]
            blocks.append([])
            blockNum += 1
        blocks[blockNum].append(entries[i])
        i += 1
    return blocks
