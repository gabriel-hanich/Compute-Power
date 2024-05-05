from func.datePoint import datePoint
from func.util import getProfile, getDateList, getDateInput, readGridDataFromFile
from datetime import datetime
import json
import matplotlib.pyplot as plt
from func.valueMaps import ValueMap
import time

profileName = "SRRPeriod"

with open("./config/download.json", "r", encoding="utf-8") as dataProfileFile:
    configData = json.load(dataProfileFile)

if profileName == "":
    profileName = getProfile(configData.keys(), "Select the profile that was used to download the data")

configData = configData[profileName]
dateList = getDateList(datetime.strptime(configData["startDate"], "%d/%m/%Y"), datetime.strptime(configData["endDate"], "%d/%m/%Y"))

for dateIndex, date in enumerate(dateList):
    dateList[dateIndex] = datePoint(date)

dataTypeCount = len(configData["dataTypes"])

startTime = time.time()
# Load data about the energy grid
print("Loading Grid Data")
if "grid" in configData["dataTypes"]:
    dataTypeCount = dataTypeCount - 1
    with open(f"./data/processed/grid/{profileName}.csv", "r") as gridDataFile:
        gridLines = gridDataFile.readlines()
        gridLabels = gridLines[0].split(",")[1:]
        

        for date in dateList:
            for rowIndex, row in enumerate(gridLines):
                if row.split(",")[0] == date.getDateStr():
                    dataArr = {}
                    for valIndex, val in enumerate(gridLabels):
                        dataArr[val] = float(row.split(",")[valIndex+1])
                    date.energyData = dataArr
                    gridLines.remove(row)
                    break
            # print(f"Loading Grid Data {str(round((rowIndex+1)/len(gridLines), 2) * 100)[:4]}%", end="\r", flush=True)
# Load Climate Data
print("Loading Climate Data")
if dataTypeCount > 0:
    with open(f"./data/processed/climate/{profileName}.csv", "r") as climateFile:
        climateData = climateFile.readlines()
        climateLabels = climateData[0].split(",")
        
        # Automatically determine the column each datatype is in
        dataIndexes = {}
        for dataType in configData["dataTypes"]:
            for labelIndex, label in enumerate(climateLabels):
                if dataType in label:
                    dataIndexes[dataType] = labelIndex
                    break
        
        # Validate that start and end dates are the same
        if not (climateData[1].split(",")[0] == dateList[0].getDateStr() and climateData[-1].split(",")[0] == dateList[-1].getDateStr()):
            print(f"FATAL ERROR\nThe Climate data and studied period do not have the same date range")
            print(f"Study Period date Range: {dateList[0].getDateStr()} - {dateList[-1].getDateStr()}")
            print(f"Climate Data date Range: {climateData[1].split(',')[0]} - {climateData[-1].split(',')[0]}")
            exit()

        # Load data
        climateData = climateData[1:] # Remove labels
        for rowIndex, row in enumerate(climateData):
            if row.split(",")[0] == dateList[rowIndex].getDateStr():
                for dataType in configData["dataTypes"]:
                    if dataType != "grid":
                        exec(f"dateList[{rowIndex}].{dataType} = float(row.split(',')[dataIndexes[dataType]])")

# Load Wind Data
print("Loading Wind Data")
if configData["windFile"] != "":
    with open(f"./data/processed/wind/{configData['windFile']}", "r") as windFile:
        windData = windFile.readlines()

        # Validate that start and end dates are the same
        if not(windData[1].split(",")[0] == dateList[0].getDateStr() and windData[-1].split(",")[0] == dateList[-1].getDateStr()):
            print(f"FATAL ERROR\nThe Wind data and studied period do not have the same date range")
            print(f"Study Period date Range: {dateList[0].getDateStr()} - {dateList[-1].getDateStr()}")
            print(f"Wind Data date Range: {windData[1].split(',')[0]} - {windData[-1].split(',')[0]}")
            exit()

        windData = windData[1:]
        for rowIndex, row in enumerate(windData):
            row = row.split(",")
            if row[0] == dateList[rowIndex].getDateStr():
                dateList[rowIndex].windspeed = float(row[1])
                dateList[rowIndex].windangle = float(row[4])

print(f"Loaded in {round(time.time() - startTime,3)} seconds")

# Now for the CLI
mainInstruction = ""
subInstruction = ""
selectedDate = datetime.strptime("01/01/1970", "%d/%m/%Y")
wipelevel = 0

# Niche settings 
doYearColor = True # Change the color of the points according to their year

while True:
    options = ["View specific Date", "Graph Something", "Exit"]
    if mainInstruction == "":
        mainInstruction = getProfile(options, "(Root) Select an Action")

    if mainInstruction == "Exit":
        break

    if mainInstruction == "View specific Date":
        if selectedDate.strftime("%d/%m/%Y") == "01/01/1970":
            print(f"(Root/View Specific Date) The data contains data from {dateList[0].getDateStr()} to {dateList[-1].getDateStr()}")
            selectedDate = getDateInput(dateList[0].date, dateList[-1].date)

            for datePoint in dateList:
                if datePoint.date == selectedDate:
                    studiedPoint = datePoint
                    break

        options = ["View Climate Data", "View Energy Data", "View Climate Map", "Select New Date", "Go Back"]
        subInstruction = getProfile(options, "\n(Root/View Specific Date/Action Select) Select an Action")

        if subInstruction == "View Climate Data":
            studiedPoint.printClimateOverview()
            
        elif subInstruction == "View Energy Data":
            studiedPoint.printGridOverview()

        elif subInstruction == "View Climate Map":
            graphTypes = configData["dataTypes"].copy()
            graphTypes.remove("grid")
            graphType = getProfile(graphTypes, "Which climate variable do you want to map?")
            climateMapData = readGridDataFromFile(f"./data/{graphType}/{selectedDate.strftime('%d.%m.%Y')}.grid")
            
            climateData = ValueMap(
                climateMapData["gridSize"], 
                climateMapData["southWestPos"],
                climateMapData["cellSize"], 
                climateMapData["noDataVal"], 
                []
            )
            climateData.setGridData(climateMapData["mapData"])
            climateData.plot(title=f"{graphType} for {selectedDate.strftime('%d/%m/%Y')}")

        if subInstruction == "Select New Date":
            wipelevel = 2
        elif subInstruction == "Go Back":
            wipelevel = 3
        else:
            wipelevel = 0
        
    if mainInstruction == "Graph Something":
        options = ["windspeed", "windangle"]
        options = options + configData["dataTypes"]
        options.append("date")
        options.append("dayoftheyear")
        xAxis = getProfile(options, "What do you want to be the X-AXIS")

        # If the User wants the X-axis to be an energy grid value
        doXAxisEnergyData = False
        if xAxis == "grid":
            options = gridLabels
            xAxis = getProfile(options, "Which energy value do you want to be the X-AXIS")
            doXAxisEnergyData = True

        options = ["windspeed", "windangle"] + configData["dataTypes"] + ["dayoftheyear"]
        yAxis = getProfile(options, "What do you want to be the Y-AXIS")

        # If the User wants the Y-axis to be an energy grid value
        doYAxisEnergyData = False
        if yAxis == "grid":
            options = gridLabels
            yAxis = getProfile(options, "Which energy value do you want to be the Y-AXIS")
            doYAxisEnergyData = True

        xVals = []
        yVals = []
        pointColors = []
        for date in dateList:
            pointColors.append(dateList[0].date.year - date.date.year)
            if doXAxisEnergyData:
                xVals.append(date.energyData[xAxis])
            else:
                exec(f"xVals.append(date.{xAxis})")
            
            if doYAxisEnergyData:
                yVals.append(date.energyData[yAxis])
            else:
                exec(f"yVals.append(date.{yAxis})")
    
        plt.xlabel(xAxis)
        plt.ylabel(yAxis)
        plt.title(f"{xAxis} vs {yAxis}")
        if xAxis == "date":
            plt.plot(xVals, yVals)
        else:
            if doYearColor:
                plt.scatter(xVals, yVals, c=pointColors, cmap='viridis')
            else:
                plt.scatter(xVals, yVals) 
        plt.show()
        plt.clf() 

        wipelevel = 3
    
    if wipelevel >= 1:
        subInstruction = ""
    if wipelevel >= 2:
        selectedDate = datetime.strptime("01/01/1970", "%d/%m/%Y")
    if wipelevel >= 3:
        mainInstruction = ""

