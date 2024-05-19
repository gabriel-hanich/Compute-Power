import os
from func.datePoint import datePoint
from func.util import getIntInput, getProfile, getDateList, getDateInput, readGridDataFromFile
from func.dataLoader import loadData
from datetime import datetime
import json
import matplotlib.pyplot as plt
from func.valueMaps import ValueMap
import time

profileName = ""

with open("./config/download.json", "r", encoding="utf-8") as dataProfileFile:
    configData = json.load(dataProfileFile)

if profileName == "":
    profileName = getProfile(configData.keys(), "Select the profile that was used to download the data")

configData = configData[profileName]
dateList = getDateList(datetime.strptime(configData["startDate"], "%d/%m/%Y"), datetime.strptime(configData["endDate"], "%d/%m/%Y"))

for dateIndex, date in enumerate(dateList):
    dateList[dateIndex] = datePoint(date)

dateList, gridLabels = loadData(profileName, configData)



# Now for the CLI
mainInstruction = ""
subInstruction = ""
selectedDate = datetime.strptime("01/01/1970", "%d/%m/%Y")
wipelevel = 0

# Niche settings 
doYearColor = True # Change the color of the points according to their year

while True:
    options = ["View specific Date", "Graph Something", "Produce Map Animation", "Exit"]
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
        xAxis = getProfile(options, "What do you want to be the X-AXIS").replace("\n", "")

        # If the User wants the X-axis to be an energy grid value
        doXAxisEnergyData = False
        if xAxis == "grid":
            options = gridLabels
            xAxis = getProfile(options, "Which energy value do you want to be the X-AXIS")
            doXAxisEnergyData = True

        options = ["windspeed", "windangle"] + configData["dataTypes"] + ["dayoftheyear"]
        yAxis = getProfile(options, "What do you want to be the Y-AXIS").replace("\n", "")

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
                try:
                    xVals.append(date.energyData[yAxis])
                except KeyError:
                    xVals.append(0)
            else:
                exec(f"xVals.append(date.{xAxis})")
            
            if doYAxisEnergyData:
                try:
                    yVals.append(date.energyData[yAxis])
                except KeyError:
                    yVals.append(0)
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
    
    if mainInstruction == "Produce Map Animation":
        wipelevel = 3
        startDate = getDateInput(dateList[0].date, dateList[-1].date, f"What date should the starting frame have? ({dateList[0].getDateStr()}-{dateList[-1].getDateStr()})")
        endDate = getDateInput(startDate, dateList[-1].date, f"What date should the ending frame have? {startDate.strftime('%d/%m/%Y')}-{dateList[-1].getDateStr()}")

        mapTypes = configData["dataTypes"].copy()
        mapTypes.remove("grid")
        mapType = getProfile(mapTypes, "Which climate variable do you want to map?")

        doSetRange = input("Do you want to use a fixed max and min value? (y/N)\n")
        graphRange = []
        if doSetRange == "y":
            graphRange.append(getIntInput(maxVal=10**10, minVal=-10**10, prompt="What is the Minimum Value\n"))
            graphRange.append(getIntInput(maxVal=10**10, minVal=graphRange[0], prompt="What is the Maximum Value\n"))

        animationName = input("What should the animation be called?\n")

        try:
            os.mkdir(f"./animations/{animationName}")
        except FileExistsError:
            doAction = input("Warning, Animation already exists, do you want to continue (y/N)\n")
            if doAction == "y":
                pass
            else:
                exit()

        frameDatelist = getDateList(startDate, endDate)
        for frameIndex, frameDate in enumerate(frameDatelist):
            climateMapData = readGridDataFromFile(f"./data/{mapType}/{frameDate.strftime('%d.%m.%Y')}.grid")
            
            climateData = ValueMap(
                climateMapData["gridSize"], 
                climateMapData["southWestPos"],
                climateMapData["cellSize"], 
                climateMapData["noDataVal"], 
                []
            )
            climateData.setGridData(climateMapData["mapData"])
            
            climateData.plot(title=f"{frameDate.strftime('%d/%m/%Y')}", path=f"./animations/{animationName}/{frameIndex}.png", range=graphRange)

            print(f"Generated Frame {frameIndex}/{len(frameDatelist)}", end="\r", flush=True)
        print("Done, You can use the following command to render the image")
        print(f"ffmpeg -r 5 -f image2 -s 1920x1080 -i %d.png -vcodec libx264 -crf 15  -pix_fmt yuv420p {animationName}.mp4")

    if wipelevel >= 1:
        subInstruction = ""
    if wipelevel >= 2:
        selectedDate = datetime.strptime("01/01/1970", "%d/%m/%Y")
    if wipelevel >= 3:
        mainInstruction = ""



    if wipelevel >= 1:
        subInstruction = ""
    if wipelevel >= 2:
        selectedDate = datetime.strptime("01/01/1970", "%d/%m/%Y")
    if wipelevel >= 3:
        mainInstruction = ""

