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