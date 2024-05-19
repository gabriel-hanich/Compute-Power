# The main thing
from func.regressor import SVRregressor, TurbineRegressor
from func.util import getProfile, getIntInput

import json
import numpy as np
import itertools
from joblib import load
from scipy.interpolate import interp1d

# Load Profiles
downloadDataProfile = "SRRPeriod"
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


# Load the SVR models
regressors = []
for model in modelFileData['models']:
    svr = load(f"./data/SVM/{modelProfile}/{model['modelType']}/svr.joblib")
    scalerX = load(f"./data/SVM/{modelProfile}/{model['modelType']}/scalerX.joblib")
    scalerY = load(f"./data/SVM/{modelProfile}/{model['modelType']}/scalerY.joblib")

    regressors.append(SVRregressor(model['modelType'], svr, scalerX, scalerY))

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
    # Determine values that will be changing
    changingVars = []
    for variable in sceneConfig["variables"].keys():
        if type(sceneConfig["variables"][variable]) == dict:
            changingVars.append(variable)

    # Calculate the variables that need to be changed
    vals = []
    for varIndex, var in enumerate(changingVars):
        valRanges = sceneConfig["variables"][var]
        vals.append(list(range(valRanges["min"], valRanges["max"], valRanges["step"])))

    print(vals)

    combinations = itertools.product(*vals)
    sceneResults = np.empty((len(vals[0]), len(changingVars)))
    a = []
    for combinationIndex, combination in enumerate(combinations):
        a.append(combination)
    test = np.array(a)
    test.reshape((len(vals[0]), len(vals[1])))
    
