# Data Processing Helpers File
#from __future__ import division

import json
import sqlite3
import predict.cve
import predict.github


CVE_ID_INDEX = 0
USERNAME_INDEX = 1
FIX_COMMIT_INDEX = 2
FIX_FILE_INDEX = 3
INTRO_COMMIT_INDEX = 4
INTRO_FILE_INDEX = 5



def insertAgreements(entry, currUserEntry):
    fixCommitAgree = "Match" if entry[FIX_COMMIT_INDEX] == currUserEntry[FIX_COMMIT_INDEX] else "Conflict"
    fixFileAgree = "Match" if entry[FIX_FILE_INDEX] == currUserEntry[FIX_FILE_INDEX] else "Conflict"
    introCommitAgree = "Match" if entry[INTRO_COMMIT_INDEX] == currUserEntry[INTRO_COMMIT_INDEX] else "Conflict"
    introFileAgree = "Match" if entry[INTRO_FILE_INDEX] == currUserEntry[INTRO_FILE_INDEX] else "Conflict"
    return (entry[CVE_ID_INDEX], entry[USERNAME_INDEX], entry[FIX_COMMIT_INDEX], fixCommitAgree, entry[FIX_FILE_INDEX], fixFileAgree, entry[INTRO_COMMIT_INDEX], introCommitAgree, entry[INTRO_FILE_INDEX], introFileAgree)

def insertPercentages(block):
    length = len(block)-1
    fixCommitCount = 0.0
    fixFileCount = 0.0
    introCommitCount = 0.0
    introFileCount = 0.0
    userEntry = block[0]
    newBlock = block
    for entry in block:
        if entry[USERNAME_INDEX] != userEntry[USERNAME_INDEX] and entry[3] == "Match":
            fixCommitCount += 1
        if entry[USERNAME_INDEX] != userEntry[USERNAME_INDEX] and entry[5] == "Match":
            fixFileCount += 1
        if entry[USERNAME_INDEX] != userEntry[USERNAME_INDEX] and entry[7] == "Match":
            introCommitCount += 1
        if entry[USERNAME_INDEX] != userEntry[USERNAME_INDEX] and entry[9] == "Match":
            introFileCount += 1
    if length > 0:
        print(length)
        print(fixCommitCount)
        newBlock[0] =(newBlock[0][0], newBlock[0][1], newBlock[0][2], str(round(fixCommitCount/length*100)) + "%", newBlock[0][3], str(round(fixFileCount/length*100)) + "%", newBlock[0][4], str(round(introCommitCount/length*100)) + "%", newBlock[0][5], str(round(introFileCount/length*100)) + "%")
    else:
        newBlock[0] =(newBlock[0][0], newBlock[0][1], newBlock[0][2], "N/A", newBlock[0][3], "N/A", newBlock[0][4], "N/A", newBlock[0][5], "N/A")
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
