from datetime import timedelta, datetime
import numpy as np

def readGridDataFromFile(path):
    # Read data from file
    with open(path, "r", encoding="utf-8") as gridFile:
        gridData = gridFile.readlines()
    
    for index, line in enumerate(gridData):
        gridData[index] = line.replace("\n", "")

    # Extract required metadata
    gridSize = [-1,-1]
    southWestPos = [-1,1]
    cellSize = -1
    noDataVal = -1
    for line in gridData:
        if "ncols" in line:
            gridSize[1] = int(line[line.find(" ")+1:])
        if "nrows" in line:
            gridSize[0] = int(line[line.find(" ")+1:])
        if "cellsize" in line:
            cellSize = float(line[line.find(" ")+1:])
        if "nodata_value" in line:
            noDataVal = float(line[line.find(" ")+1:])
        if "SOUTHWEST LATITUDE" in line:
            line = line.replace(" ", "")
            southWestPos[0] = float(line[line.find("LATITUDE")+8:])
        if "SOUTHWEST LONGITUDE" in line:
            line = line.replace(" ", "")
            southWestPos[1] = float(line[line.find("LONGITUDE")+9:])
    

    # Put grid data into a np array
    mapData = np.empty((gridSize[0], gridSize[1]))

    rowIndex = 0 
    for line in gridData:
        row = line.split(" ")
        try:
            testVal = float(row[0]) # Ensure that the first value is a float, thus only considering values
            for itemIndex, item in enumerate(row):
                dataVal = float(item)
                if (dataVal == noDataVal) or (dataVal < 0): # Replace all NODATAVALS with 0
                    mapData[rowIndex][itemIndex] = 0
                else:
                    mapData[rowIndex][itemIndex] = dataVal
            
            rowIndex = rowIndex + 1
        except ValueError: # If line contains metadata instead of GRID data
            pass

    return {"gridSize": gridSize, "southWestPos": southWestPos, "cellSize": cellSize, "noDataVal": noDataVal, "mapData": mapData}

def getBOMURL(dataDate, dataType):
    downloadDate = dataDate.strftime("%Y%m%d%Y%m%d")
    if dataType == "irradiance":
        return f"http://www.bom.gov.au/web03/ncc/www/awap/solar/solarave/daily/grid/0.05/history/nat/{downloadDate}.grid.Z"
    if dataType == "temperature":
        return f"http://www.bom.gov.au/web03/ncc/www/awap/temperature/maxave/daily/grid/0.05//history/nat/{downloadDate}.grid.Z"
    if dataType == "pressure":
        return f"http://www.bom.gov.au/web03/ncc/www/awap/vprp/vprph09/daily/grid/0.05/history/nat/{downloadDate}.grid.Z"
    if dataType == "rainfall":
        return f"http://www.bom.gov.au/web03/ncc/www/awap/rainfall/totals/daily/grid/0.05/history/nat/{downloadDate}.grid.Z"
    
def getIntInput(maxVal, minVal=0, prompt=""):
    # Get an input from the user that is a valid integer 
    while True:
        val = input(prompt)
        try:
            val = int(val)
            if val >= minVal and val <= maxVal:
                return val
            else:
                raise ValueError
        except ValueError:
            print(f"This is an invalid input, the input must be an integer between {minVal} and {maxVal}")

def getDateList(startDate, endDate, delta=1):
    # Get a list of dates between 2 dates (inclusive)
    dateList = []
    currentDate = startDate
    while currentDate <= endDate:
        dateList.append(currentDate)
        currentDate += timedelta(days=delta)
    return dateList

def getProfile(keys, prompt="Select a profile"):
    if len(keys) == 1:
        return list(keys)[0]

    print(prompt)
    for keyIndex, key in enumerate(keys):
        print(f"{keyIndex+1}. {key}")
    return list(keys)[getIntInput(len(keys), 0, "")-1]

def getDateInput(minVal, maxDate, prompt="Select a date"):
    while True:
        potentialDate = input(prompt + "\n")
        try:
            userDate = datetime.strptime(potentialDate, "%d/%m/%Y")
            if userDate >= minVal and userDate <= maxDate:
                return userDate
            else:
                print("Date is not within range")
        except ValueError:
            print("Invalid Date")

def calculateRMSE(predicted, observed):
    if len(predicted) != len(observed):
        print("ERROR, two lists aren't the same length")
        
    rmse = 0
    for valIndex, val in enumerate(predicted):
        rmse = float(rmse + (predicted[valIndex] - observed[valIndex])**2)
        
    rmse = rmse/len(predicted)
    return rmse ** 0.5

def predict(xValue, scalerX, scalerY, svr):
    transformedVal = scalerX.transform(xValue)
    predictedVal = svr.predict(transformedVal)
    val = scalerY.inverse_transform(predictedVal.reshape(1, -1))
    return val

def getTrainingRow(datePoint, modelType):
    row = [
        datePoint.dayoftheyear,
        datePoint.temperature,
        datePoint.irradiance,
        datePoint.pressure,
        datePoint.rainfall,
    ]
    if modelType == "demand":
        row.append(datePoint.energyData["au.nem.nsw1.demand.energy (GWh)"])
    elif modelType == "rooftop_solar":
        row.append(datePoint.energyData["Normalized Rooftop Solar (GWh)"])
    elif modelType == "utility_solar":
        row.append(datePoint.energyData["Normalized Utility Solar (GWh)"])
    elif modelType == "wind":
        row.append(datePoint.energyData["au.nem.nsw1.fuel_tech.wind.energy (GWh)"])
    return row

def trapezoidalRule(x, y):
    area = 0
    for xIndex, xVal in enumerate(x):
        if xIndex != len(x) - 1:
            # 0.5 * h * (y1+y2)
            area += 0.5 * abs(xVal - x[xIndex+1]) * (y[xIndex] + y[xIndex+1])
        
    return area