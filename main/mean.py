from func.valueMaps import ValueMap
from func.util import readGridDataFromFile, getDateList, getProfile
import json
from datetime import datetime
import numpy as np
import pandas as pd 

# Load Profiles
meanProfile = ""
dateProfile = ""
units = {"temperature": "Celcius", "irradiance": "MJ/m^2", "pressure": "hPa", "rainfall": "mm", "density": "count"}

# Load the 2 config files
with open("./config/mean.json") as meanFile:
    meanData = json.load(meanFile)

with open("./config/download.json") as dateFile:
    dateData = json.load(dateFile)

# Select a profile if one hasn't already been selected
if meanProfile == "":
    meanProfile = getProfile(meanData.keys(), "Select a mean profile (mean.json)")
if dateProfile == "":
    dateProfile = getProfile(dateData.keys(), "Select a date profile (download.json)")

print(f"Selected {meanProfile} profile for location data")
print(f"Selected {dateProfile} profile for source data")

meanData = meanData[meanProfile]
dateData = dateData[dateProfile]

# Convert dates from strings to datetime objs & generate list of included dates
dateData["startDate"] = datetime.strptime(dateData["startDate"], "%d/%m/%Y")
dateData["endDate"] = datetime.strptime(dateData["endDate"], "%d/%m/%Y")

dateList = getDateList(dateData["startDate"], dateData["endDate"], dateData["frequency"])

# Load density data
densityFileData = readGridDataFromFile("./data/density/compressedDensity.grid")
densityData = ValueMap(
    densityFileData["gridSize"], 
    densityFileData["southWestPos"],
    densityFileData["cellSize"], 
    densityFileData["noDataVal"], 
    "count"
    )
densityData.setGridData(densityFileData["mapData"])


# Convert bounding Lat/Lon to a list of array indexes that fall within the bounding box
boundingCoords = np.array(meanData["coords"])

boundingIndexes = np.empty(boundingCoords.shape)
for coordIndex, coord in enumerate(boundingCoords):
    boundingIndexes[coordIndex] = densityData.getCoord(coord[0], coord[1])

samplePoints = densityData.getInternalCoords(boundingIndexes)

# Create first row of .csv file
outputData = [[]]
for dataType in dateData["dataTypes"].copy():
    outputData[0].append(f"{dataType} ({units[dataType]})")
outputData[0].insert(0, "Date")

if meanData["isBounding"]: # If generating a population-weighted mean
    # Calculate the total population of the bounding box
    totalPopulation = 0
    for point in samplePoints:
        totalPopulation += densityData.gridData[point[0]][point[1]]

    # Determine mean values for every day
    for dateIndex, date in enumerate(dateList):
        outputData.append([date.strftime('%d/%m/%Y')])
        for dataIndex, dataType in enumerate(dateData["dataTypes"]):
            # Load the climate data file
            climateFileData = readGridDataFromFile(f"./data/{dataType}/{date.strftime('%d.%m.%Y')}.grid")
            climateData = ValueMap(
                climateFileData["gridSize"], 
                climateFileData["southWestPos"],
                climateFileData["cellSize"], 
                climateFileData["noDataVal"], 
                units[dataType]
            )
            climateData.setGridData(climateFileData["mapData"])

            # Calculate mean 
            valueSum = 0
            for point in samplePoints:
                latLon = densityData.getLatLon(point[1], point[0]) # Get Latitude and Longitude of the sample point
                densityVal = densityData.gridData[point[0]][point[1]] # Get the number of people that live at the given lat/lon
                climateVal = climateData.determineValue(latLon[0], latLon[1]) # Get the climate value at the given lat/lon

                valueSum += climateVal * densityVal
            
            meanVal = valueSum/totalPopulation

            outputData[-1].append(str(meanVal))

            print(f"Loaded {str(round((len(dateData['dataTypes']) * dateIndex + dataIndex+1)/(len(dateList)*len(dateData['dataTypes'])), 4)*100)[0:4]}%", end="\r", flush=True)

else:  # If the user only cares about a value at a single location
    lat, lon = meanData["coords"][0]
    print(f"Looking at single point, {lat}, {lon}")
    for dateIndex, date in enumerate(dateList):
        outputData.append([date.strftime('%d/%m/%Y')])
        for dataIndex, dataType in enumerate(dateData["dataTypes"]):
            # Load the climate data file
            climateFileData = readGridDataFromFile(f"./data/{dataType}/{date.strftime('%d.%m.%Y')}.grid")
            climateData = ValueMap(
                climateFileData["gridSize"], 
                climateFileData["southWestPos"],
                climateFileData["cellSize"], 
                climateFileData["noDataVal"], 
                units[dataType]
            )
            climateData.setGridData(climateFileData["mapData"])
            outputData[-1].append(str(climateData.determineValue(lat, lon)))

            print(f"Loaded {str(round((len(dateData['dataTypes']) * dateIndex + dataIndex+1)/(len(dateList)*len(dateData['dataTypes'])), 4)*100)[0:4]}%", end="\r", flush=True)

# Output data to .csv file
with open(f"./data/processed/{dateProfile}.csv", "w+", encoding="utf-8") as outputFile:
    for line in outputData:
        outputFile.write(",".join(line)+"\n")

print(f"Written {len(outputData)} lines to data/processed/{dateProfile}.csv")
