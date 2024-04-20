from func.valueMaps import ValueMap
from func.util import readGridDataFromFile, getDateList, getProfile
import json
from datetime import datetime
import numpy as np
import pandas as pd 

# Determine average values for the downloaded .grid files

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

dataTypes = dateData["dataTypes"].copy()
doGrid = False
if "grid" in dataTypes:
    doGrid = True
    dataTypes.remove("grid")

# Create first row of .csv file
outputData = [[]]
for dataType in dataTypes:
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
        for dataIndex, dataType in enumerate(dataTypes):
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
        for dataIndex, dataType in enumerate(dataTypes):
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


# Output climate data to .csv file
            print(f"Loaded {str(round((len(dateData['dataTypes']) * dateIndex + dataIndex+1)/(len(dateList)*len(dateData['dataTypes'])), 5)*100)[0:5]}%", end="\r", flush=True)
with open(f"./data/processed/climate/{dateProfile}.csv", "w+", encoding="utf-8") as outputFile:
    for line in outputData:
        outputFile.write(",".join(line)+"\n")

print(f"Written {len(outputData)} lines to data/processed/climate/{dateProfile}.csv")

# If the User includes grid data 
if doGrid:
    gridLabels = ["date"]
    gridDataArr = {}

    # Get an inclusive list containing every year in the studied period
    yearList = list(year+dateData["startDate"].year for year in range(dateData["endDate"].year - dateData["startDate"].year+1))

    for yearIndex, year in enumerate(yearList):
        # Load Electricity Grid data for the given year
        with open(f"./data/grid/generation/{year}.json", "r") as yearFile:
            yearData = json.load(yearFile)["data"]
        
        for rowIndex, row in enumerate(yearData):
            # Make a list of all the data labels
            if f"{row['id']} ({row['units']})" not in gridLabels:
                gridLabels.append(f"{row['id']} ({row['units']})")
            
            # Add the years worth of data points into correct column
            try:
                gridDataArr[f"{row['id']} ({row['units']})"] = gridDataArr[f"{row['id']} ({row['units']})"] + row["history"]["data"]
            except KeyError:
                gridDataArr[f"{row['id']} ({row['units']})"] = row["history"]["data"]
    
    missingList = []
    with open(f"./data/processed/grid/{dateProfile}.csv", "w") as outputFile:
        # The first row of the CSV is the grid labels
        rowCount = 0
        outputFile.write(",".join(gridLabels) + "\n")
        for dateIndex, date in enumerate(dateList):
            # The first column of every row is the date
            row = [date.strftime("%d/%m/%Y")]
            for label in gridLabels:
                if label != "date":
                    try:
                        row.append(str(gridDataArr[label][dateIndex]))
                    except IndexError:
                        # This can occur if the tracked variables change across the different years
                        if f"{date.year} {label}" not in missingList:
                            print(f"   Not enough data points for {date.year} {label}")
                            missingList.append(f"{date.year} {label}")
                        row.append("0")
            outputFile.write(",".join(row) + "\n")
            rowCount += 1
    print(f"Written {rowCount} lines to data/processed/grid/generation/{dateProfile}.csv")
    


