# Train the Required SVMs
from func.util import getProfile, getTrainingRow, predict
from func.dataLoader import loadData

import json
import numpy as np
import os

from joblib import dump
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


trainingProfile = ""
dataProfile = ""

# Load the 2 config files
with open("./config/model.json") as trainingFile:
    trainingConfig = json.load(trainingFile)

with open("./config/download.json") as dataFile:
    dataRegister = json.load(dataFile)

# Select a profile if one hasn't already been selected
if trainingProfile == "":
    trainingProfile = getProfile(dataRegister.keys(), "Select a mean profile (mean.json)")
if dataProfile == "":
    dataProfile = getProfile(dataRegister.keys(), "Select a date profile (download.json)")

print(f"Selected {trainingProfile} profile for SVR Training Inputs")
print(f"Selected {dataProfile} profile for source data")

trainingConfig = trainingConfig[trainingProfile]
configData = dataRegister[dataProfile]

dateList, gridLabels = loadData(dataProfile, configData)

labels = [
    "Day of the Year",
    "Temperature",
    "Irradiance",
    "Pressure",
    "Rainfall",
    "Observed Value",
    "Predicted Value",
    "Delta"
]

print(" ")

for model in trainingConfig["models"]:
    inputData = np.empty((len(dateList), 6))

    # Read values from dictionary
    kernelStr = model["kernel"]
    testValCount = model["testValCount"]
    cVal = model["cVal"]
    gammaVal = model["gammaVal"]

    # Convert datePoints into a numpy array
    for dateIndex, date in enumerate(dateList):
        inputData[dateIndex] = getTrainingRow(date, model["modelType"])
    
    # Shuffle the array and divide it into training and evaluation datasets
    np.random.shuffle(inputData)
    trainingData, evaluateData = inputData[:len(dateList)-testValCount,:], inputData[len(dateList)-testValCount:,:]

    # Scale the training and test data to center it on (0,0) with appropriate std. dev
    scalerX = StandardScaler()
    scalerY = StandardScaler()
    trainX = scalerX.fit_transform(trainingData[:, :5])
    trainY = scalerY.fit_transform(trainingData[:,5].reshape(-1, 1))
    testX = scalerX.fit_transform(evaluateData[:, :5])
    testY = scalerY.fit_transform(evaluateData[:,5].reshape(-1, 1))

    # Fit the model and evaluate it
    svr = SVR(kernel=kernelStr, C=cVal, gamma=gammaVal)
    svr.fit(trainX, trainY.ravel())
    
    rSquared = svr.score(testX, testY) 
    print(f"Model for {model['modelType']} achieved an R^2 value of {rSquared}")

    print(f"Dumping SVR {model['modelType']} Model")


    # Write SVR model and scalers to file
    # Make new directory if it doesn't already exist
    try:
        os.mkdir(f"./data/SVM/{trainingProfile}")
    except FileExistsError:
        pass
    try:
        os.mkdir(f"./data/SVM/{trainingProfile}/{model['modelType']}")
    except FileExistsError:
        pass

    dump(svr, f"./data/SVM/{trainingProfile}/{model['modelType']}/svr.joblib")
    dump(scalerX, f"./data/SVM/{trainingProfile}/{model['modelType']}/scalerX.joblib")
    dump(scalerY, f"./data/SVM/{trainingProfile}/{model['modelType']}/scalerY.joblib")

    if model["doDataDump"]:
        print(f"Dumping ALL data for {model['modelType']} model")
        # If the user has requested a large scale data dump
        with open(f"./data/SVM/{trainingProfile}/{model['modelType']}/predictions.csv", "w") as outputFile:
            outputFile.write(",".join(labels) + "\n")
            for row in inputData:
                predictedVal = predict(
                    row[:5].reshape(1, -1), 
                    scalerX, 
                    scalerY, 
                    svr
                )
                csvRow = ''
                for val in row:
                    csvRow = csvRow + str(val) + ","
                csvRow = csvRow + str(predictedVal[0][0]) + ","
                csvRow = csvRow + str(predictedVal[0][0]-row[5]) + ","
                outputFile.write(csvRow + "\n")
    print('')
print(f"Trained and Dumped data for {len(trainingConfig['models'])} Model")