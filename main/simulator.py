# The main thing
from func.datePoint import datePoint
from func.regressor import SVRregressor, TurbineRegressor
from func.util import getProfile, getIntInput

import json
import numpy as np
import itertools
from joblib import load
from datetime import datetime
import time

# Load Profiles
downloadDataProfile = ""
modelProfile = "SRRPeriod"
simulationProfiles = []

units = {"temperature": "Celcius", "irradiance": "MJ/m^2", "pressure": "hPa", "rainfall": "mm", "density": "count"}

# Load the 2 config files
with open("./config/download.json") as downloadFile:
    downloadData = json.load(downloadFile)
with open("./config/model.json") as modelFile:
    modelFileData = json.load(modelFile)
with open("./config/simulation.json")as simulationFile:
    simulationConfig = json.load(simulationFile)

# Select a profile if one hasn't already been selected
if downloadDataProfile == "":
    downloadDataProfile = getProfile(downloadData.keys(), "Select a download profile (download.json)")
if modelProfile == "":
    modelProfile = getProfile(modelFileData.keys(), "Select a model profile (model.json)")
if simulationProfiles == []:
    if len(simulationConfig.keys()) == 1:
        simulationProfiles.append(list(simulationConfig.keys())[0])
    else:
        selectedProfileCount = getIntInput(len(simulationConfig.keys()), 1, "How many scenarios do you want to run?\n")
        for _ in range(selectedProfileCount):
            name = getProfile(simulationConfig.keys(), "Select a simulation profile (model.json)")
            simulationProfiles.append(name)

print(f"Selected {downloadDataProfile} profile for Download data Model")
print(f"Selected {modelProfile} profile for SVR Model")
print(f"Selected {','.join(simulationProfiles)} profile for scenarios")

modelFileData = modelFileData[modelProfile]
downloadData = downloadData[downloadDataProfile]

energyKeys = {
    "demand":"au.nem.nsw1.demand.energy (GWh)",
    "rooftop_solar": "au.nem.nsw1.fuel_tech.solar_rooftop.energy (GWh)",
    "utility_solar": "au.nem.nsw1.fuel_tech.solar_utility.energy (GWh)"
}

startTime = time.time()

# Load the SVR models
regressors = []
for model in modelFileData['models']:
    svr = load(f"./data/SVM/{modelProfile}/{model['modelType']}/svr.joblib")
    scalerX = load(f"./data/SVM/{modelProfile}/{model['modelType']}/scalerX.joblib")
    scalerY = load(f"./data/SVM/{modelProfile}/{model['modelType']}/scalerY.joblib")

    regressors.append(SVRregressor(model['modelType'], svr, scalerX, scalerY))


results = {}
for simulationName in simulationProfiles:
    sceneConfig = simulationConfig[simulationName]
    
    # Initialise wind production model
    # Load wind turbine curve
    with open(f"./data/grid/wind/{sceneConfig['turbineName']}.csv", "r") as generationCurveFile:
        fileLines = generationCurveFile.readlines()
    generationCurve = np.empty((len(fileLines)-1, 2))
    for lineIndex, line in enumerate(fileLines):
        if lineIndex != 0:
            thisLine = line.split(",")
            try:
                generationCurve[lineIndex-1] = [float(thisLine[0]), float(thisLine[1].replace('\n', ''))]
            except ValueError:
                generationCurve[lineIndex-1] = [0,0]
    
    # Create wind turbines with different angles
    windTurbines = []
    tCount = sceneConfig["turbineCount"]
    for i in range(tCount):
        direction = sceneConfig["meanTurbineDirection"] + ((i-(tCount*0.5))/tCount)*2*sceneConfig["turbineDirectionRange"]
        
        if direction < 0:
            direction = 360+direction
        elif direction > 360:
            direction = direction-360

        windTurbines.append(
            TurbineRegressor(
                f"{sceneConfig['turbineName']}-{i}",
                generationCurve,
                direction
            )
        )

    # Run the model
    dateVals = []
    results[simulationName] = []
    if sceneConfig["useRealClimateVar"]:
        # Values change based on real climate data
        startDate = datetime.strptime(sceneConfig["variables"]["startDate"], "%d/%m/%Y")
        endDate = datetime.strptime(sceneConfig["variables"]["endDate"], "%d/%m/%Y")
        with open(f"./data/processed/climate/{downloadDataProfile}.csv", "r") as climateFile:
            for lineIndex, line in enumerate(climateFile.readlines()):
                if lineIndex != 0:
                    vals = line.split(",")
                    thisDate = datetime.strptime(vals[0], "%d/%m/%Y")
                    if thisDate > startDate and thisDate < endDate:
                        thisDateVal = datePoint(
                            thisDate,
                            float(vals[2]),
                            float(vals[1]),
                            float(vals[3]),
                            float(vals[4]),
                            0, 
                            0,
                            {},
                            str(lineIndex)
                        )
                        dateVals.append(thisDateVal)

        with open(f"./data/processed/wind/{downloadDataProfile}.csv") as windData:
            for lineIndex, line in enumerate(windData.readlines()):
                if lineIndex != 0:
                    lineVals = line.split(",")
                    searchDate = datetime.strptime(lineVals[0], "%d/%m/%Y")
                    if searchDate > startDate and searchDate < endDate:
                        for dateVal in dateVals:
                            if dateVal.date == searchDate:
                                dateVal.windspeed = float(lineVals[1])
                                dateVal.windangle = float(lineVals[4])

    else:
        # Values change based on config settings
        changingVars = []
        for variable in sceneConfig["variables"].keys():
            if type(sceneConfig["variables"][variable]) == dict:
                changingVars.append(variable)

        # Calculate the variables that need to be changed
        vals = []
        for varIndex, var in enumerate(changingVars):
            valRanges = sceneConfig["variables"][var]
            vals.append(list(range(valRanges["min"], valRanges["max"], valRanges["step"])))

        combinations = itertools.product(*vals)
        combinationCount = len(list(itertools.product(*vals)))
        
    

        for combinationIndex, combination in enumerate(combinations):
            # Create date to train
            instanceData = {"id": str(combinationIndex)}
            for parameter in sceneConfig["variables"]:
                try:
                    cIndex = changingVars.index(parameter)
                    instanceData[parameter] = combination[cIndex]
                except ValueError:
                    instanceData[parameter] = sceneConfig["variables"][parameter]

            thisDateVal = datePoint(
                instanceData["dayOfTheYear"],
                instanceData["temperature"],
                instanceData["irradiance"],
                instanceData["pressure"],
                instanceData["rainfall"],
                instanceData["windspeed"],
                instanceData["windangle"],
                {},
                instanceData["id"],
            )
            dateVals.append(thisDateVal)

    combinationCount = len(dateVals)
    for dateIndex, dateVal in enumerate(dateVals):
        # Do Regressor Stuff
        energyData = {}
        for regressor in regressors:
            val = regressor.predict(dateVal)
            if regressor.regressorType == "rooftop_solar" or regressor.regressorType == "utility_solar":
                val = val * sceneConfig["solarCapacity"]
            energyData[energyKeys[regressor.regressorType]] = val[0][0]

        # Determine Wind Data
        windGen = 0
        for turbine in windTurbines:
            windGen += turbine.predictOutput(dateVal.windspeed, dateVal.windangle, sceneConfig["turbinesYaw"])
        # Needed to convert KW to GwH
        energyData["au.nem.nsw1.fuel_tech.wind.energy (GWh)"] = (windGen / 1000000) * 24

        dateVal.energyData = energyData

        results[simulationName].append(dateVal)

        print(f"Loading {dateIndex}/{combinationCount} for scenario {simulationName}", end="\r", flush=True)


    windPortion = 0
    portionCount = 0
    # Write Data to File
    with open(f"./data/processed/sim/{simulationName}.json", "w", encoding="utf-8") as outputFile:
        res = []
        for date in results[simulationName]:
            dateData = date.getDict()
            windPortion += dateData["windPortion"]
            portionCount += 1
            res.append(dateData)
        json.dump(res, outputFile, indent=4) 
    print(f"\n{simulationName} has a mean wind portion of {round(windPortion/portionCount, 6)}")

print("\n")

print(f"Loaded in {round(time.time() - startTime, 3)} Seconds")