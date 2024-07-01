import os
from func.datePoint import datePoint
from func.util import getIntInput, getProfile, getDateList, getDateInput, readGridDataFromFile
from func.dataLoader import loadData
from datetime import datetime
import json
import matplotlib.pyplot as plt
from func.valueMaps import ValueMap
import numpy as np
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

dateList, gridLabels = loadData(profileName, configData)



# Now for the CLI
mainInstruction = ""
subInstruction = ""
selectedDate = datetime.strptime("01/01/1970", "%d/%m/%Y")
wipelevel = 0

# Niche settings 
doYearColor = True # Change the color of the points according to their year

while True:
    options = ["View specific Date", "Graph Something", "View Simulation Data","Produce Map Animation", "Exit"]
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
        yearsList = []
        for date in dateList:
            pointColors.append(dateList[0].date.year - date.date.year)
            if date.date.year not in yearsList:
                yearsList.append(date.date.year)

            if doXAxisEnergyData:
                try:
                    xVals.append(date.energyData[xAxis])
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
                yearsList.reverse()
                a = plt.scatter(xVals, yVals, c=pointColors, cmap='viridis')
                # plt.legend(handles=scatter.legend_elements()[0], labels=classes)
                plt.legend(handles=a.legend_elements()[0], labels=yearsList)
            else:
                plt.scatter(xVals, yVals) 
        plt.show()
        plt.clf() 

        wipelevel = 3
    
    if mainInstruction == "View Simulation Data":
        wipelevel = 3
        simFiles = os.listdir("./data/processed/sim")
        simProfiles = []
        for simFile in simFiles:
            if ".json" in simFile:
                simProfiles.append(simFile)
        simProfile = getProfile(simProfiles, "(Sim) Select an Simulation Profile")    
        print(f"Loading {simProfile} data")
        with open(f"./data/processed/sim/{simProfile}") as simFile:
            simData = json.load(simFile)

        options = list(simData[0].keys())
        xAxis = getProfile(options, "(Sim) What do you want the X-Axis to be?")
        xGrid = False
        if xAxis == "grid":
            xGrid = True
            xAxis = getProfile(simData[0]['grid'].keys(), "(Sim) What do you want the X-Axis to be?")
        
        yAxis = getProfile(options, "(Sim) What do you want the Y-Axis to be?")
        yGrid = False
        if yAxis == "grid":
            yGrid = True
            yAxis = getProfile(simData[0]['grid'].keys(), "(Sim) What do you want the X-Axis to be?")

        color = getProfile(options, "(Sim) What attribute should control dot color?")

        x = []
        y = []
        c = []
        for instance in simData:
            if xGrid:
                x.append(instance["grid"][xAxis])
            else:
                x.append(instance[xAxis])

            if yGrid:
                y.append(instance["grid"][yAxis])
            else:
                y.append(instance[yAxis])

            c.append(float(instance[color]))

        print(f"Graphing {xAxis} against {yAxis}. Pearsons Value of {round(np.corrcoef(x, y)[0,1], 5)}")

        # Color maps: https://matplotlib.org/stable/users/explain/colors/colormaps.html

        cmap = ""
        if cmap == "":
            cmap = input("cmap:") 

        plt.scatter(x, y, c=list(c), cmap=cmap)
        plt.xlabel(xAxis)
        plt.ylabel(yAxis)
        cbar = plt.colorbar()

        cbar.set_label(color)

        doGraphImg = input("y/N Do You want to export a .png of the graph?\n")
        if doGraphImg.lower() == "y":
            if not os.path.exists(f"../manualAnalysis/{simProfile.replace('.json', '')}/"):
                os.makedirs(f"../manualAnalysis/{simProfile.replace('.json', '')}/")
            fileName = input('File Title:')
            plt.savefig(f"../manualAnalysis/{simProfile.replace('.json', '')}/{fileName}.png", dpi=800)
            print(f"File Saved to ../manualAnalysis/{simProfile.replace('.json', '')}/{fileName}.png")

        plt.show()
        plt.clf()
        

        doExport = input("y/N Do you want to export the data to a .csv file?\n")
        if doExport.lower() == "y":
            with open(f"./data/processed/sim/{simProfile.replace('.json', '')}.csv", "w") as outputFile:
                labels = list(simData[0].keys())
                labels.remove("grid")
                labels = labels + list(simData[0]["grid"].keys())
                for labelIndex, label in enumerate(labels):
                    labels[labelIndex] = label.replace(".", "-")

                outputFile.write(",".join(labels))
                for row in simData:
                    vals = []
                    for key in labels:
                        try:
                            vals.append(str(row[key]))
                        except KeyError:
                            vals.append(str(row["grid"][key.replace("-", ".")]))
                    outputFile.write("\n" + ",".join(vals))

            print(f"Exported to ./data/processed/sim/{simProfile.replace('.json', '')}.csv")

        
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

