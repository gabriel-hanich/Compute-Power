import requests
import unlzw3 as unlzw
from datetime import datetime
from func.util import getBOMURL, getIntInput, getDateList, getProfile
import json
import time
import os.path

# Automatically download BOM climate data 

k_profile = ""
k_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}

# Load config data
with open("./config/download.json") as configFile:
    configData = json.load(configFile)

# From the config data, load the appropritate profile
# If the profile is not specified, ask the user
if k_profile == "":
    k_profile = getProfile(configData.keys())

k_setup = configData[k_profile]

print(f"Selected {k_profile} Profile")

startTime = time.time()

# Convert start and end dates into a list of included dates 
k_setup["startDate"] = datetime.strptime(k_setup["startDate"], "%d/%m/%Y")
k_setup["endDate"] = datetime.strptime(k_setup["endDate"], "%d/%m/%Y")
k_datesList = getDateList(k_setup["startDate"], k_setup["endDate"], k_setup["frequency"])

fileCount = 0


for dataTypeIndex, dataType in enumerate(k_setup["dataTypes"]):
    for dateIndex, date in enumerate(k_datesList):
        filePath = f"data/{dataType}/{date.strftime('%d.%m.%Y')}.grid" # The path at which the file will be saved
        if not ((os.path.isfile(filePath)) and (not k_setup["overRideFiles"])): # Check if the file exists AND that the user has opted to override the save
            url = getBOMURL(date, dataType)

            res = requests.get(url, headers=k_headers, stream=True)
            data = unlzw.unlzw(res.content).decode("utf-8") # Unzip the file
            splitData = data.split("\n")

            # Write the file
            with open(filePath, "w", encoding='utf-8') as outputFile:
                outputFile.writelines([string.strip() + '\n' for string in splitData])
            fileCount += 1 # Record number of files created

        print(f"{dateIndex+1}/{len(k_datesList)} Loaded for {dataTypeIndex+1}/{len(k_setup['dataTypes'])}", end="\r", flush=True)


print(f"Finished downloading {fileCount} files in {round(time.time() -startTime, 2)} seconds")