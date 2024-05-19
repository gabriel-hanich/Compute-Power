from func.util import getDateList
from func.datePoint import datePoint

from datetime import datetime
import time

def loadData(profileName, configData, doPrintOuts=True):
    startTime = time.time()
    dataTypeCount = len(configData["dataTypes"])
    dateList = getDateList(datetime.strptime(configData["startDate"], "%d/%m/%Y"), datetime.strptime(configData["endDate"], "%d/%m/%Y"))

    for dateIndex, date in enumerate(dateList):
        dateList[dateIndex] = datePoint(date)
        # Load data about the energy grid
    print("Loading Grid Data")
    if "grid" in configData["dataTypes"]:
        dataTypeCount = dataTypeCount - 1
        with open(f"./data/processed/grid/{profileName}.csv", "r") as gridDataFile:
            gridLines = gridDataFile.readlines()
            gridLabels = gridLines[0].replace("\n","").split(",")[1:]

            for date in dateList:
                for rowIndex, row in enumerate(gridLines):
                    if row.split(",")[0] == date.getDateStr():
                        dataArr = {}
                        for valIndex, val in enumerate(gridLabels):
                            try:
                                dataArr[val] = float(row.split(",")[valIndex+1])
                            except ValueError:
                                print(row)
                                dataArr[val] = 0
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
    return dateList, gridLabels