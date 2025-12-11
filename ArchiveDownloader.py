from math import e
from operator import contains
import os
import requests
import json
import urllib
import re
import pikepdf

ROOT = "https://www.archive.org"
HISTORY_FILE = "history.json"
DOWNLOAD_DIR = "Downloads"
UPLOAD_DIR = "Uploads"

def getMetadata(id):
    metadata = "metadata"

    metadataUrl = f'{ROOT}/{metadata}/{id}'
    retryCount = 3

    for i in range(retryCount):
        response = requests.get(metadataUrl)

        if response.status_code == 200:
            return response.json()

    return None

def loadHistory():
    history = dict()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE,"r") as json_file:
            history = json.load(json_file)

    return history

def createDownloadDirectory():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

def createUploadDirectory():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

def getFilename(id,history,metadata):
    for file in metadata['files']:
        if ".pdf" in file["name"]:
            if not file["name"] in history[id]:
               return file["name"]
    return ""

def downloadFile(id,filename):
    download = "download"
    safeFilename =urllib.parse.quote(filename, safe='') 
    downloadURL = f'{ROOT}/{download}/{id}/{safeFilename}'
    retryCount = 3
     
    for i in range(retryCount):
        response = requests.get(downloadURL)
    
        if response.status_code == 200:
            localFile = GetLocalFilename(filename)
            with open(localFile,"wb") as file:
                file.write(response.content)
            return localFile
    return ""

def GetLocalFilename(filename):
    return f"{DOWNLOAD_DIR}/{filename}"

def ApplyMetadata(filename,pattern,series):
    localFilename = GetLocalFilename(filename)
    issueMatch = re.match(pattern,filename)
    issueName = "-".join(issueMatch.groups())
    newfilename = f"{UPLOAD_DIR}/{series} {issueName}.pdf"

    pdf = pikepdf.Pdf.open(localFilename)
    pdf.docinfo["/Author"] = series
    pdf.docinfo["/Title"] = issueName
    pdf.save(newfilename)
    pdf.close()
    os.remove(localFilename)

    

def SaveHistory(history):
    with open(HISTORY_FILE,"w") as json_file:
        json.dump(history,json_file)

id = "1982-10-byte-magazine-october-1-byte-magazine-21533"
series = "Byte Magazine" # Possibly get this from Archive.org...
issueNamePattern = r"^(\d{4}) (\d{2})"

history = loadHistory()

if not id in history:
    history[id] = []

createDownloadDirectory()
createUploadDirectory()

metadata = getMetadata(id)

if metadata is None:
    exit

filename = getFilename(id,history,metadata)

if filename is None or len(filename) == 0:
    exit

downloadedFile = downloadFile(id,filename)
if downloadedFile is not None and len(downloadedFile) > 0:
    ApplyMetadata(filename,issueNamePattern,series)
    history[id].append(filename)
    SaveHistory(history)
